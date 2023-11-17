import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="k1TTens",
  database="vepkar2"
)

print(mydb)

mycursor = mydb.cursor()

sql_allvepslemmas = "SELECT * FROM lemmas WHERE lang_id=1"
mycursor.execute(sql_allvepslemmas)

lemmas = []

myresult = mycursor.fetchall()

column_names = mycursor.column_names

for row in myresult:
    entry = {}
    for idx, ctitle in enumerate(column_names):
        entry[ctitle] = row[idx]
    lemmas.append(entry)

print(lemmas[:10])



mydb.close()


# def findsequenceinlemmas(listoflemmas, listofvowels, atbeginning=True):
#     for lemma_entry in listoflemmas:


def getvowellist(word):
    word_modified = ""
    for i in range(len(word)):
        if word[i] not in ["a", "o", "i", "e", "u", "ü", "ä", "ö", "õ", "ɨ", "y"]:
            word_modified += "."
        else:
            word_modified += word[i]
    vowellist = word.split(".")
