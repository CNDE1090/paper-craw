from src.crawing import ArtiCraw as ac

pmid = ac.search_articles("cancer", retmax=5, year_range=(2010, 2020))

abstracts = ac.fetch_abstract(pmid[0])
print(abstracts)