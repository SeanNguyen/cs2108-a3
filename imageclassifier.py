import cv2, csv, json, cherrypy
from subprocess import call
from os import chdir, path
from nltk.stem import WordNetLemmatizer
import cPickle as pickle
import numpy as np

def get_image_index(index_file):
    indexlist = []
    with open(index_file, "rb") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            indexlist.append(row)
    return indexlist

def add_to_index_file(index_file, img, tags):
    with open(index_file, "a") as csvfile:
        csvwriter = csv.writer(csvfile)
        line = [img] + tags
        csvwriter.writerow(line)

def get_image_semantics(image_path, image_name):
    semantics_path = image_path+image_name.replace(".jpg","") + ".txt"
    with open(semantics_path, "rb") as semantics_file:
        for row in semantics_file:
            return row.split(" ")

def find_top_10_tags(images, top_images):
    print "performing lemmatizing and retrieving top 10 tags"
    word = WordNetLemmatizer()
    tagtotals = {}
    for img, sim in top_images:
        for tag in images[img].tags:
            tag = word.lemmatize(tag)
            if tag in tagtotals:
                tagtotals[tag] += 1
            else:
                tagtotals[tag] = 1
    temp = []
    for tag in tagtotals.keys():
        temp.append((tag, tagtotals[tag]))
    temp = sorted(temp, key=lambda tag: tag[1])
    return temp[len(temp)-10:]

def pickle_keypoints(keypoints, descriptors):
    i = 0
    temp_array = []
    for point in keypoints:
        temp = (point.pt, point.size, point.angle, point.response, point.octave,
        point.class_id, descriptors[i])     
        ++i
        temp_array.append(temp)
    return temp_array

def unpickle_keypoints(array):
    keypoints = []
    descriptors = []
    for point in array:
        temp_feature = cv2.KeyPoint(x=point[0][0],y=point[0][1],_size=point[1], _angle=point[2], _response=point[3], _octave=point[4], _class_id=point[5])
        temp_descriptor = point[6]
        keypoints.append(temp_feature)
        descriptors.append(temp_descriptor)
    return keypoints, np.array(descriptors)

def get_sift_descriptors(sift, img_name, image_path, load=True):
    sift_file = image_path+img_name.replace(".jpg","") + ".sift"
    if not path.exists(sift_file):
        img = cv2.imread(image_path+img_name,0)
        kp, des = sift.detectAndCompute(img,None)
        temp = pickle_keypoints(kp, des)
        pickle.dump(temp, open(sift_file, "wb"))
        return (kp, des)
    elif load:
        temp = pickle.load(open(sift_file, "rb"))
        return unpickle_keypoints(temp)
    return
    
class Image:

    def __init__(self, filename, tags, visual_hist):
        self.filename = filename
        self.tags = tags
        self.visual_hist = visual_hist

    def compare_visual_sim(self, c_visual_hist):
        sim = 0
        for i in range(1000):
            if (float(self.visual_hist[i]) > 0 and float(c_visual_hist[i]) > 0):
                sim += 1 - abs(float(self.visual_hist[i]) - float(c_visual_hist[i]))
        return sim
            
    def cosine_sim(self, c_visual_hist):
        dot_product = 0.0
        norm_a = 0.0
        norm_b = 0.0
        for i in range(1000):
            dot_product += float(self.visual_hist[i]) * float(c_visual_hist[i]);
            norm_a += float(self.visual_hist[i]) ** 2
            norm_b += float(c_visual_hist[i]) ** 2
        return dot_product / ((norm_a ** 0.5) * (norm_b ** 0.5))

    def __str__(self):
        return "%s, %s, %s" % (self.filename, len(self.tags), len(self.visual_hist))

class ImageClassifier:

    train_dir = "./webserver/uploads/"
    train_index = "train.csv" 

    def __init__(self):
        self.images = {}
        self.sift = cv2.SIFT()
        self.__load_training_data()

        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks=50)   # or pass empty dictionary

        self.flann = cv2.FlannBasedMatcher(index_params,search_params)

    def __load_training_data(self):
        indexlist = get_image_index(self.train_index)
        i = 0
        for row in indexlist:
            if i % 100 == 0: print "loading %s of %s" % (i, len(indexlist))
            semantics = get_image_semantics(self.train_dir, row[0])
            image = Image(row[0], row[1:], semantics)
            self.images[row[0]] = image
            #just make sure there exists the serialized file. too large to load all into memory.
            get_sift_descriptors(self.sift, row[0], self.train_dir, load=False)
            i += 1
        print "training images loaded"

    def __process_semantics(self, file_name, file_path):
        print "retrieving visual semantic features"
        semantics_file = file_path+file_name.replace(".jpg","") + ".txt"
        if not path.exists(semantics_file):
            inputfile = open("./semanticFeature/temp.txt", "w")
            absfilepath = path.abspath(file_path+file_name)
            inputfile.write(absfilepath)
            inputfile.close()
            chdir("./semanticFeature")
            return_code = call("image_classification.exe temp.txt")
            chdir("../")
        return get_image_semantics(file_path, file_name)

    def __sift_match_rank(self, file_name, candidates, file_path):
        img1 = cv2.imread(file_path+file_name,0)
        kp1, des1 = self.sift.detectAndCompute(img1,None)
        sift_match_rank = []
        for img_name, sim in candidates:
            kp2, des2 = get_sift_descriptors(self.sift, img_name, self.train_dir)
            if des1 is not None and des2 is not None and len(des1) > 0 and len(des2) > 0:
                matches = self.flann.knnMatch(des1,des2,k=2)
                i = 0
                # ratio test as per Lowe's paper
                for i,(m,n) in enumerate(matches):
                    if m.distance < 0.7*n.distance:
                        i += 1
                sift_match_rank.append((img_name, i+sim))
        sift_match_rank = sorted(sift_match_rank, key=lambda s: s[1])
        return sift_match_rank[len(sift_match_rank)-50:]

    def __narrow_candidates(self, file_name, candidates, file_path):
        print "narrowing candidate results through good sift flann matches"
        return self.__sift_match_rank(file_name, candidates, file_path)

    def classify_image(self, file_name, file_path=train_dir):
        semantics = self.__process_semantics(file_name, file_path)
        ranking = Ranking(semantics, self.images)
        candidates = ranking.get_top_compare() + ranking.get_top_cosine()
        candidates = self.__narrow_candidates(file_name, candidates, file_path)
        tags = find_top_10_tags(self.images, candidates)
        print tags
        return [tag[0] for tag in tags]

    def add_image(self, img, tags):
        add_to_index_file(self.train_index, img, tags)
        semantics = self.__process_semantics(img, self.train_dir)
        image = Image(img, tags, semantics)
        self.images[img] = image
        

class Ranking:

    def __init__(self, query, train):
        print "performing ranking based on visual semantic features"
        self.rank_compare = self.__rank_compare(query, train)
        self.rank_cosine = self.__rank_consine(query, train)

    def __rank_compare(self, query, train):
        rank = []
        for key in train.keys():
            sim = train[key].compare_visual_sim(query)
            rank.append((key, sim))
        rank = sorted(rank, key=lambda key_sim: key_sim[1])
        return rank
        
    def __rank_consine(self, query, train):
        rank = []
        for key in train.keys():
            sim = train[key].cosine_sim(query)
            rank.append((key, sim))
        rank = sorted(rank, key=lambda key_sim: key_sim[1])
        return rank

    def get_top_compare(self):
        return self.rank_compare[len(self.rank_compare)-50:]

    def get_top_cosine(self):
        return self.rank_cosine[len(self.rank_compare)-50:]

class Restful_api(object):

    def __init__(self, ic):
        self.ic = ic
        
    @cherrypy.expose
    def index(self):
        return "test index please ignore"

    @cherrypy.expose
    def get_tags(self, img=""):
        results = self.ic.classify_image(img)
        return json.dumps({"tags" : results})

    @cherrypy.expose
    def set_tags(self, img="", tags={}):
        tags = json.loads(tags)
        self.ic.add_image(img, tags["tags"])
        return ""

def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"

if __name__ == "__main__":
    ic = ImageClassifier()
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 1111,})
    conf = {'/': {'tools.CORS.on': True}}
    cherrypy.quickstart(Restful_api(ic), '/', conf)
