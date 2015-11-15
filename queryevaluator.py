from imageclassifier import *
from nltk.stem import WordNetLemmatizer
import csv

query_path = "./query/"
query_index = "query.csv"
result_file = "results.csv"

def test_queries(ic, word):
    i = 0
    query_list = get_image_index(query_index)
    with open(result_file, "wb") as csvfile:
        csvwriter = csv.writer(csvfile)
        for query in query_list:
            print "processing query %s of %s" % (i, len(query_list))
            tags = ic.classify_image(query[0], query_path)
            (actual, total) = find_intersection(query[1:], tags, word)
            row = [query[0], actual, total] + tags
            csvwriter.writerow(row)
            print "%s out of %s tags matched" % (actual, total)
            i+=1

def find_intersection(query_tags, result_tags, word):
    [word.lemmatize(tag) for tag in query_tags]
    query_tags = set(query_tags)
    total = len(query_tags)
    result = query_tags.intersection(result_tags)
    print "matched %s" % result
    actual = len(result)
    return (actual, total)

if __name__ == "__main__":

    word = WordNetLemmatizer()
    ic = ImageClassifier()
    test_queries(ic, word)
