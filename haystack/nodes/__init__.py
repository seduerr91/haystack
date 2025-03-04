from haystack.utils.import_utils import safe_import

from haystack.nodes.base import BaseComponent

from haystack.nodes.answer_generator import BaseGenerator, RAGenerator, Seq2SeqGenerator
from haystack.nodes.document_classifier import BaseDocumentClassifier, TransformersDocumentClassifier
from haystack.nodes.evaluator import EvalDocuments, EvalAnswers
from haystack.nodes.extractor import EntityExtractor, simplify_ner_for_qa
from haystack.nodes.file_classifier import FileTypeClassifier
from haystack.nodes.file_converter import (
    BaseConverter,
    DocxToTextConverter,
    ImageToTextConverter,
    MarkdownConverter,
    PDFToTextConverter,
    PDFToTextOCRConverter,
    TikaConverter,
    TikaXHTMLParser,
    TextConverter,
    AzureConverter,
    ParsrConverter,
)
from haystack.nodes.other import Docs2Answers, JoinDocuments, RouteDocuments, JoinAnswers
from haystack.nodes.preprocessor import BasePreProcessor, PreProcessor
from haystack.nodes.query_classifier import SklearnQueryClassifier, TransformersQueryClassifier
from haystack.nodes.question_generator import QuestionGenerator
from haystack.nodes.ranker import BaseRanker, SentenceTransformersRanker
from haystack.nodes.reader import BaseReader, FARMReader, TransformersReader, TableReader, RCIReader
from haystack.nodes.retriever import (
    BaseRetriever,
    DensePassageRetriever,
    EmbeddingRetriever,
    ElasticsearchRetriever,
    ElasticsearchFilterOnlyRetriever,
    TfidfRetriever,
    Text2SparqlRetriever,
    TableTextRetriever,
)
from haystack.nodes.summarizer import BaseSummarizer, TransformersSummarizer
from haystack.nodes.translator import BaseTranslator, TransformersTranslator

Crawler = safe_import("haystack.nodes.connector.crawler", "Crawler", "crawler")  # Has optional dependencies
