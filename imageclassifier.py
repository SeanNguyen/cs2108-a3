import cv2, csv, json, cherrypy
from subprocess import call
from os import chdir, path
from nltk.stem import WordNetLemmatizer

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
        csvwriter.write(line)

def get_image_semantics(image_path, image_name):
    semantics_path = image_path + image_name.replace(".jpg", ".txt")
    with open(semantics_path, "rb") as semantics_file:
        for row in semantics_file:
            return row.split(" ")

def find_top_10_tags(images, top_images):
    "performing lemmatizing and retrieving top 10 tags"
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
        self.__load_training_data()
        self.sift = cv2.SIFT()

        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks=50)   # or pass empty dictionary

        self.flann = cv2.FlannBasedMatcher(index_params,search_params)

    def __load_training_data(self):
        indexlist = get_image_index(self.train_index)
        for row in indexlist:
            semantics = get_image_semantics(self.train_dir, row[0])
            image = Image(row[0], row[1:], semantics)
            self.images[row[0]] = image

    def __process_semantics(self, file_name):
        print "retrieving visual semantic features"
        if not path.exists(self.train_dir+file_name.replace(".jpg",".txt")):
            inputfile = open("./semanticFeature/temp.txt", "w")
            absfilepath = path.abspath(self.train_dir+file_name)
            inputfile.write(absfilepath)
            inputfile.close()
            chdir("./semanticFeature")
            return_code = call("image_classification.exe temp.txt")
            chdir("../")
        return get_image_semantics(self.train_dir, file_name)

    def __sift_match_rank(self, file_name, candidates):
        img1 = cv2.imread(self.train_dir+file_name,0)
        kp1, des1 = self.sift.detectAndCompute(img1,None)
        sift_match_rank = []
        for img_name, sim in candidates:
            img2 = cv2.imread(self.train_dir+img_name,0)
            kp2, des2 = self.sift.detectAndCompute(img2,None)

            matches = self.flann.knnMatch(des1,des2,k=2)
            i = 0
            # ratio test as per Lowe's paper
            for i,(m,n) in enumerate(matches):
                if m.distance < 0.7*n.distance:
                    i += 1
            sift_match_rank.append((img_name, i))
        sift_match_rank = sorted(sift_match_rank, key=lambda s: s[1])
        return sift_match_rank[len(sift_match_rank)-50:]

    def __narrow_candidates(self, file_name, candidates):
        print "narrowing candidate results through secondary sift ranking"
        return self.__sift_match_rank(file_name, candidates)

    def classifyImage(self, file_name):
        semantics = self.__process_semantics(file_name)
        ranking = Ranking(semantics, self.images)
        candidates = ranking.get_top_compare() + ranking.get_top_cosine()
        candidates = self.__narrow_candidates(file_name, candidates)
        tags = find_top_10_tags(self.images, candidates)
        print tags
        return [tag[0] for tag in tags]

    def add_image(self, img, tags):
        add_to_index_file(self.train_index, img, tags)
        

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
        results = self.ic.classifyImage(img)
        return json.dumps({"tags" : results})

    @cherrypy.expose
    def set_tags(self, img="", tags={}):
        tags = json.loads(tags)
        self.ic.add_image(img, tags["tags"])
        return ""

if __name__ == "__main__":

    ic = ImageClassifier()
    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'server.socket_port': 1111,})
    cherrypy.quickstart(Restful_api(ic), '/') 

