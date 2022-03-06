def article_nlp(self, text, language):
    # Load English tokenizer, tagger, parser and NER
    nlp = spacy.load('%s_core_web_sm' % language)
    doc = nlp(text)
    nouns = [chunk.text for chunk in doc.noun_chunks]

    endpoint = SPARQL("https://query.wikidata.org/sparql")

    nouns = [noun.replace("\n", " ").strip() for noun in nouns]
    # building the query string
    values = [' '.join([f'"{noun}"@' + language for noun in nouns[n * 50:n * 50 + 50]]) for n in
              range((len(nouns) // 50) + 1)]

    queryValueFormatTags = '%s\n' * (len(values))
    entryQueryStr = """

    """
    entryQueryStr = entryQueryStr % ("\n".join(values))

    entryQuery = Query(query=entryQueryStr,
                       name="Recognized entries",
                       lang="sparql")
    entryQueryResLoD = endpoint.queryAsListOfDicts(entryQuery.query)

    return entryQueryResLoD