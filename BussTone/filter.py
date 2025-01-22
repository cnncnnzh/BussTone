import pandas
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm

KEYWORDS = [
    'California Consumer Privacy Act',
    'Data Privacy',
    'General Data Protection Regulation',
    #'Personal Information',
    #'Compliance Requirements',
    #'Data Protection Laws',
]

def cosine_similarity(x, y):
    cosine = np.dot(x, y)/(norm(x)*norm(y))
    return cosine

def get_score_contriever(sentences):
    model = AutoModel.from_pretrained('facebook/contriever')
    tokenizer = AutoTokenizer.from_pretrained('facebook/contriever')

    inputs_sentences = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')
    inputs_keywords = tokenizer(KEYWORDS, padding=True, truncation=True, return_tensors='pt')
    # Compute token embeddings
    outputs_sentences = model(**inputs_sentences)
    outputs_keywords = model(**inputs_keywords)

    # Mean pooling
    def mean_pooling(token_embeddings, mask):
        token_embeddings = token_embeddings.masked_fill(~mask[..., None].bool(), 0.)
        sentence_embeddings = token_embeddings.sum(dim=1) / mask.sum(dim=1)[..., None]
        return sentence_embeddings
    sentence_embeddings = mean_pooling(outputs_sentences[0], inputs_sentences['attention_mask'])
    keyword_embeddings = mean_pooling(outputs_keywords[0], inputs_keywords['attention_mask'])
    sentence_embeddings = sentence_embeddings.detach().numpy()
    keyword_embeddings = keyword_embeddings.detach().numpy()
    results = np.zeros([len(sentences), len(KEYWORDS)])
    for i, sentence in enumerate(sentence_embeddings):
        results[i,:] = np.array([cosine_similarity(sentence, keyword) for keyword in keyword_embeddings])
    return results

def get_score_sentence_transformers(sentences, transformer):
    model = SentenceTransformer(transformer)
    sentence_embeddings = model.encode(sentences)
    keyword_embeddings = model.encode(KEYWORDS)
    results = np.zeros([len(sentences), len(KEYWORDS)])
    for i, sentence in enumerate(sentence_embeddings):
        results[i,:] = np.array([cosine_similarity(sentence, keyword) for keyword in keyword_embeddings])
    return results

def find_sentences(sentences):    
    sentence_count = 10
    bottom_score = 0.4
    if len(sentences) >= sentence_count:   
        res1 = get_score_contriever(sentences)
        res2 = get_score_sentence_transformers(sentences, 'all-MiniLM-L6-v2')
        res3 = get_score_sentence_transformers(sentences, 'BAAI/bge-m3')
        res4 = get_score_sentence_transformers(sentences, "sentence-transformers/all-mpnet-base-v2")

        avg_score = (res1 + res2 + res3 + res4) / 4
        max_scores = avg_score.max(axis=1)    
    
        final_sentences = []
        print(max_scores)
        top_ten_score_indices = max_scores.argsort()[::-1][:sentence_count]
        for index in top_ten_score_indices:
            if max_scores[index] > bottom_score:
                final_sentences.append(sentences[index])
        return final_sentences
    else:
        return sentences
    

if __name__ == "__main__":
    sentences = [
        'Data privacy and data protection are areas of increasing state legislative focus.',
        'For example, in June of 2018, the Governor of California signed into law the\nCalifornia Consumer Privacy Act of 2018 (the “CCPA”).',
        'The CCPA, which became effective on January 1, 2020, applies to for-profit businesses that conduct business\nin California and meet certain revenue or data collection thresholds.',
        'The CCPA will give consumers the right to request disclosure of information collected about\nthem, and whether that information has been sold or shared with others, the right to request deletion of personal information (subject to certain exceptions), the right\nto opt out of the sale of the consumer’s personal information, and the right not to be discriminated against for exercising these rights.',
        'The CCPA contains several\nexemptions, including an exemption applicable to information that is collected, processed, sold or disclosed pursuant to the Gramm-Leach-Bliley Act. The California\nAttorney General has proposed, but not yet adopted\nregulations implementing the CCPA, and the California State Legislature has amended the Act since its passage.',
        'Comerica has a physical footprint in California and\nwill be required to comply with the CCPA. In addition, similar laws may be adopted by other states where Comerica does business. The federal government may also\npass data privacy or data protection legislation.\n',
        'In this article, we calculate the Cosine Similarity between the two non-zero vectors.',
    ]
    res = find_sentences(sentences)
    print(res)