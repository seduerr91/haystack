from haystack.document_stores import ElasticsearchDocumentStore

from haystack.nodes import EmbeddingRetriever
from haystack.utils import launch_es, print_answers, fetch_archive_from_http
import pandas as pd
import requests
import logging
import subprocess
import time


def tutorial4_faq_style_qa():
    ## "FAQ-Style QA": Utilizing existing FAQs for Question Answering

    # While *extractive Question Answering* works on pure texts and is therefore more generalizable, there's also a common alternative that utilizes existing FAQ data.
    #
    # Pros:
    # - Very fast at inference time
    # - Utilize existing FAQ data
    # - Quite good control over answers
    #
    # Cons:
    # - Generalizability: We can only answer questions that are similar to existing ones in FAQ
    #
    # In some use cases, a combination of extractive QA and FAQ-style can also be an interesting option.
    launch_es()

    ### Init the DocumentStore
    # In contrast to Tutorial 1 (extractive QA), we:
    #
    # * specify the name of our `text_field` in Elasticsearch that we want to return as an answer
    # * specify the name of our `embedding_field` in Elasticsearch where we'll store the embedding of our question and that is used later for calculating our similarity to the incoming user question
    # * set `excluded_meta_data=["question_emb"]` so that we don't return the huge embedding vectors in our search results

    document_store = ElasticsearchDocumentStore(
        host="localhost",
        username="",
        password="",
        index="document",
        embedding_field="question_emb",
        embedding_dim=384,
        excluded_meta_data=["question_emb"],
        similarity="cosine",
    )

    ### Create a Retriever using embeddings
    # Instead of retrieving via Elasticsearch's plain BM25, we want to use vector similarity of the questions (user question vs. FAQ ones).
    # We can use the `EmbeddingRetriever` for this purpose and specify a model that we use for the embeddings.
    #
    retriever = EmbeddingRetriever(
        document_store=document_store, embedding_model="sentence-transformers/all-MiniLM-L6-v2", use_gpu=True
    )

    # Download a csv containing some FAQ data
    # Here: Some question-answer pairs related to COVID-19
    doc_dir = "data/tutorial4"
    s3_url = "https://s3.eu-central-1.amazonaws.com/deepset.ai-farm-qa/datasets/documents/small_faq_covid.csv.zip"
    fetch_archive_from_http(url=s3_url, output_dir=doc_dir)

    # Get dataframe with columns "question", "answer" and some custom metadata
    df = pd.read_csv(f"{doc_dir}/small_faq_covid.csv")
    # Minimal cleaning
    df.fillna(value="", inplace=True)
    df["question"] = df["question"].apply(lambda x: x.strip())
    print(df.head())

    # Get embeddings for our questions from the FAQs
    questions = list(df["question"].values)
    df["question_emb"] = retriever.embed_queries(texts=questions)
    df = df.rename(columns={"question": "content"})

    # Convert Dataframe to list of dicts and index them in our DocumentStore
    docs_to_index = df.to_dict(orient="records")
    document_store.write_documents(docs_to_index)

    # Initialize a Pipeline (this time without a reader) and ask questions

    from haystack.pipelines import FAQPipeline

    pipe = FAQPipeline(retriever=retriever)

    prediction = pipe.run(query="How is the virus spreading?", params={"Retriever": {"top_k": 10}})
    print_answers(prediction, details="medium")


if __name__ == "__main__":
    tutorial4_faq_style_qa()

# This Haystack script was made with love by deepset in Berlin, Germany
# Haystack: https://github.com/deepset-ai/haystack
# deepset: https://deepset.ai/
