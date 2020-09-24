"""
Made Satria Wibawa @2020
"""
import re
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
import docx
import fitz
import numpy as np

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

basedir = os.path.abspath(os.path.dirname(__file__))


class corpusSimID:
    """Pairwise Cosine Similarity among Indonesian documents.
    corpusSimID(self, path=file_directory, file_type="text")

    Compute cosine similarity among Indonesian documents with TF-IDF.

    Parameters
    --------------

        path : directory all located document. example: "C:/doc/data"
        file_type : file type of documents. "word" for Microsoft Word documents. File extension .docx. "pdf" for PDF file. File extension .pdf. "text" for text file. File extension .txt
    """

    def __init__(self, path, stem="yes", file_type="text"):
        files = os.listdir(path)
        self.path = path
        if file_type == "text":
            self.files = [i for i in files if i.endswith(".txt")]
        elif file_type == "word":
            self.files = [i for i in files if i.endswith(".docx")]
        elif file_type == "pdf":
            self.files = [i for i in files if i.endswith(".pdf")]
        self.file_type = file_type
        self.stem = stem

    def __len__(self):
        """return number of documents"""
        return len(self.files)

    def get_doc(self, filename):
        """Extract text from docx file"""
        doc = docx.Document(self.path + filename)
        fullText = []
        for para in doc.paragraphs:
            text = para.text
            text = (text.rstrip()).lstrip()
            text = text.replace("\n", " ")
            fullText.append(text)
        return " ".join(fullText)

    def get_pdf(self, filename):
        """Extract text from pdf file"""
        doc = fitz.open(self.path + filename)
        fullText = []
        for i in range(doc.pageCount):
            text = doc.getPageText(i)
            text = (text.rstrip()).lstrip()
            text = text.replace("\n", " ")
            fullText.append(text)
        return " ".join(fullText)

    def get_text(self, filename):
        """Extract text from txt file"""
        with open(self.path + filename) as file:
            text = file.read().replace("\n", " ")
        return text

    def get_file(self):
        return self.files

    def get_corpus(self):
        """Extract corpus from documents

        Return 2d python list
            1st column: file name
            2nd column: words in i-th document after tokenization
            3rd column: words in i-th document after stemming
        """
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()

        text_files = []

        for i in range(len(self.files)):
            if self.file_type == "word":
                rawText = self.get_doc(self.files[i])
            elif self.file_type == "pdf":
                rawText = self.get_pdf(self.files[i])
            elif self.file_type == "text":
                rawText = self.get_text(self.files[i])
            procText = re.sub("[^A-Za-z0-9]+", " ", rawText).lower()
            if self.stem == "yes":
                procText = stemmer.stem(rawText)
            text_files.append([self.files[i], rawText, procText])

        return text_files

    def get_tfidf(self):
        """Extract TF-IDF features from corpus

        Return two variables
            1st variable: tf-idf in 2d array. column is number of document, row is feature
            2nd variable: words list in corpus
        """
        rawData = self.get_corpus()
        corpus = [column[2] for column in rawData]

        vectorizer = TfidfVectorizer()
        x = vectorizer.fit_transform(corpus)

        return x.toarray(), vectorizer.get_feature_names()

    def get_similarity(self):
        """Calculate pairwise similarity among documents based on cosine similarity

        Return similarity matrix
        """
        corpus, _ = self.get_tfidf()
        return cosine_similarity(corpus)

    def visualize(self, labels=True, cmap="YlGnBu"):
        """Visualize similarity heatmap

        visualize(self, label=True, cmap="YlGnBu")

        Return similarity matrix in heatmap plot.

        Parameters
        --------------

            label: show label in x and y axis. True is shown, False not shown
            cmap: colormap for heatmap. see https://matplotlib.org/examples/color/colormaps_reference.html for colormap list
        """
        sim = self.get_similarity()
        plt.figure(figsize=(10, 8))
        plt.title("Similarity Heatmap")
        if labels:
            sns.set(font_scale=0.8)
            sns.heatmap(
                sim * 100,
                cmap=cmap,
                fmt=".2f",
                linewidth=0.1,
                annot=True,
                xticklabels=self.files,
                yticklabels=self.files,
            )
        else:
            sns.heatmap(sim, cmap=cmap, linewidth=0.2, annot=True)
        plt.xticks(rotation="vertical")
        plt.yticks(rotation="horizontal")
        plt.show()

    def saveviz(self, fname, cmap="coolwarm"):
        """Method for save image and serve in Flask"""
        plt.switch_backend("agg")
        sim = self.get_similarity()
        plt.figure(figsize=(25, 25))
        plt.title("Similarity Heatmap")
        sns.heatmap(
            sim,
            cmap=cmap,
            fmt=".2f",
            linewidth=0.1,
            annot=True,
            xticklabels=self.files,
            yticklabels=self.files,
            annot_kws={"size": 6},
        )
        plt.xticks(rotation="vertical")
        plt.yticks(rotation="horizontal")
        plt.savefig(basedir + "/static/images/{}.png".format(fname))
        plt.close()

    def get_dataframe(self):
        sim = self.get_similarity()
        fList = self.get_file()
        df = pd.DataFrame(np.zeros((len(sim) * len(sim), 3)),
                          columns=["a", "b", "c"])
        k = 0
        for i in range(len(sim)):
            for j in range(len(sim)):
                df.iloc[k, 0] = fList[i]
                df.iloc[k, 1] = fList[j]
                df.iloc[k, 2] = sim[i][j]
                k = k + 1
        df["c"] = (df["c"] * 100).round(2)
        return df


if __name__ == "__main__":
    directory = input("Enter directory file: ")
    file_type = input("Enter file type (word/pdf/text): ").lower()
    if file_type not in ("word", "pdf", "text"):
        print("Unknown file type !")
    if not (os.path.exists(directory)):
        print("Directory not found !")
    if (os.path.exists(directory)) and (file_type in ("word", "pdf", "text")):
        data = corpusSimID(directory + "/", "no", file_type)
        data.visualize()
