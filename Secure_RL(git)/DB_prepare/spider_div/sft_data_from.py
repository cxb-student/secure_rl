import json
import os
import re
import random
import sqlparse
import difflib
from typing import List, Optional, Tuple
from rapidfuzz import fuzz
import sqlite3
import functools
from nltk.tokenize import word_tokenize
from nltk import ngrams
from sql_metadata import Parser
from pyserini.search.lucene import LuceneSearcher
from func_timeout import func_set_timeout, FunctionTimedOut

random.seed(42)


def detect_special_char(name):
    for special_char in ['(', '-', ')', ' ', '/']:
        if special_char in name:
            return True

    return False


def add_quotation_mark(s):
    return "`" + s + "`"


def get_db_schema_sequence(schema):
    schema_sequence = "database schema :\n"
    for table in schema["schema_items"]:
        table_name, table_comment = table["table_name"], table["table_comment"]
        if detect_special_char(table_name):
            table_name = add_quotation_mark(table_name)

        # if table_comment != "":
        #     table_name += " ( comment : " + table_comment + " )"

        column_info_list = []
        for column_name, column_type, column_comment, column_content, pk_indicator in \
                zip(table["column_names"], table["column_types"], table["column_comments"], table["column_contents"],
                    table["pk_indicators"]):
            if detect_special_char(column_name):
                column_name = add_quotation_mark(column_name)
            additional_column_info = []
            # column type
            additional_column_info.append(column_type)
            # pk indicator
            if pk_indicator != 0:
                additional_column_info.append("primary key")
            # column comment
            if column_comment != "":
                additional_column_info.append("comment : " + column_comment)
            # representive column values
            if len(column_content) != 0:
                pass

            column_info_list.append(table_name + "." + column_name + " ( " + " | ".join(additional_column_info) + " )")

        schema_sequence += "table " + table_name + " , columns = [ " + " , ".join(column_info_list) + " ]\n"

    if len(schema["foreign_keys"]) != 0:
        schema_sequence += "foreign keys :\n"
        for foreign_key in schema["foreign_keys"]:
            for i in range(len(foreign_key)):
                if detect_special_char(foreign_key[i]):
                    foreign_key[i] = add_quotation_mark(foreign_key[i])
            schema_sequence += "{}.{} = {}.{}\n".format(foreign_key[0], foreign_key[1], foreign_key[2], foreign_key[3])
    else:
        schema_sequence += "foreign keys : None\n"

    return schema_sequence.strip()


_stopwords = {'who', 'ourselves', 'down', 'only', 'were', 'him', 'at', "weren't", 'has', 'few', "it's", 'm', 'again',
              'd', 'haven', 'been', 'other', 'we', 'an', 'own', 'doing', 'ma', 'hers', 'all', "haven't", 'in', 'but',
              "shouldn't", 'does', 'out', 'aren', 'you', "you'd", 'himself', "isn't", 'most', 'y', 'below', 'is',
              "wasn't", 'hasn', 'them', 'wouldn', 'against', 'this', 'about', 'there', 'don', "that'll", 'a', 'being',
              'with', 'your', 'theirs', 'its', 'any', 'why', 'now', 'during', 'weren', 'if', 'should', 'those', 'be',
              'they', 'o', 't', 'of', 'or', 'me', 'i', 'some', 'her', 'do', 'will', 'yours', 'for', 'mightn', 'nor',
              'needn', 'the', 'until', "couldn't", 'he', 'which', 'yourself', 'to', "needn't", "you're", 'because',
              'their', 'where', 'it', "didn't", 've', 'whom', "should've", 'can', "shan't", 'on', 'had', 'have',
              'myself', 'am', "don't", 'under', 'was', "won't", 'these', 'so', 'as', 'after', 'above', 'each', 'ours',
              'hadn', 'having', 'wasn', 's', 'doesn', "hadn't", 'than', 'by', 'that', 'both', 'herself', 'his',
              "wouldn't", 'into', "doesn't", 'before', 'my', 'won', 'more', 'are', 'through', 'same', 'how', 'what',
              'over', 'll', 'yourselves', 'up', 'mustn', "mustn't", "she's", 're', 'such', 'didn', "you'll", 'shan',
              'when', "you've", 'themselves', "mightn't", 'she', 'from', 'isn', 'ain', 'between', 'once', 'here',
              'shouldn', 'our', 'and', 'not', 'too', 'very', 'further', 'while', 'off', 'couldn', "hasn't", 'itself',
              'then', 'did', 'just', "aren't"}
# fmt: on

_commonwords = {"no", "yes", "many"}


def is_number(s: str) -> bool:
    try:
        float(s.replace(",", ""))
        return True
    except:
        return False


def is_stopword(s: str) -> bool:
    return s.strip() in _stopwords


def is_commonword(s: str) -> bool:
    return s.strip() in _commonwords


def is_common_db_term(s: str) -> bool:
    return s.strip() in ["id"]


class Match(object):
    def __init__(self, start: int, size: int) -> None:
        self.start = start
        self.size = size


def is_span_separator(c: str) -> bool:
    return c in "'\"()`,.?! "


def split(s: str) -> List[str]:
    return [c.lower() for c in s.strip()]


def prefix_match(s1: str, s2: str) -> bool:
    i, j = 0, 0
    for i in range(len(s1)):
        if not is_span_separator(s1[i]):
            break
    for j in range(len(s2)):
        if not is_span_separator(s2[j]):
            break
    if i < len(s1) and j < len(s2):
        return s1[i] == s2[j]
    elif i >= len(s1) and j >= len(s2):
        return True
    else:
        return False


def get_effective_match_source(s: str, start: int, end: int) -> Match:
    _start = -1

    for i in range(start, start - 2, -1):
        if i < 0:
            _start = i + 1
            break
        if is_span_separator(s[i]):
            _start = i
            break

    if _start < 0:
        return None

    _end = -1
    for i in range(end - 1, end + 3):
        if i >= len(s):
            _end = i - 1
            break
        if is_span_separator(s[i]):
            _end = i
            break

    if _end < 0:
        return None

    while _start < len(s) and is_span_separator(s[_start]):
        _start += 1
    while _end >= 0 and is_span_separator(s[_end]):
        _end -= 1

    return Match(_start, _end - _start + 1)


def get_matched_entries(
        s: str, field_values: List[str], m_theta: float = 0.85, s_theta: float = 0.85
) -> Optional[List[Tuple[str, Tuple[str, str, float, float, int]]]]:
    if not field_values:
        return None

    if isinstance(s, str):
        n_grams = split(s)
    else:
        n_grams = s

    matched = dict()
    for field_value in field_values:
        if not isinstance(field_value, str):
            continue
        fv_tokens = split(field_value)
        sm = difflib.SequenceMatcher(None, n_grams, fv_tokens)
        match = sm.find_longest_match(0, len(n_grams), 0, len(fv_tokens))
        if match.size > 0:
            source_match = get_effective_match_source(
                n_grams, match.a, match.a + match.size
            )
            if source_match:  # and source_match.size > 1
                match_str = field_value[match.b: match.b + match.size]
                source_match_str = s[
                                   source_match.start: source_match.start + source_match.size
                                   ]
                c_match_str = match_str.lower().strip()
                c_source_match_str = source_match_str.lower().strip()
                c_field_value = field_value.lower().strip()
                if c_match_str and not is_common_db_term(c_match_str):  # and not is_number(c_match_str)
                    if (
                            is_stopword(c_match_str)
                            or is_stopword(c_source_match_str)
                            or is_stopword(c_field_value)
                    ):
                        continue
                    if c_source_match_str.endswith(c_match_str + "'s"):
                        match_score = 1.0
                    else:
                        if prefix_match(c_field_value, c_source_match_str):
                            match_score = fuzz.ratio(c_field_value, c_source_match_str) / 100
                        else:
                            match_score = 0
                    if (
                            is_commonword(c_match_str)
                            or is_commonword(c_source_match_str)
                            or is_commonword(c_field_value)
                    ) and match_score < 1:
                        continue
                    s_match_score = match_score
                    if match_score >= m_theta and s_match_score >= s_theta:
                        if field_value.isupper() and match_score * s_match_score < 1:
                            continue
                        matched[match_str] = (
                            field_value,
                            source_match_str,
                            match_score,
                            s_match_score,
                            match.size,
                        )

    if not matched:
        return None
    else:
        return sorted(
            matched.items(),
            key=lambda x: (1e16 * x[1][2] + 1e8 * x[1][3] + x[1][4]),
            reverse=True,
        )


@functools.lru_cache(maxsize=1000, typed=False)
def get_column_picklist(table_name: str, column_name: str, db_path: str) -> list:
    fetch_sql = "SELECT DISTINCT `{}` FROM `{}`".format(column_name, table_name)
    try:
        conn = sqlite3.connect(db_path)
        conn.text_factory = bytes
        c = conn.cursor()
        c.execute(fetch_sql)
        picklist = set()
        for x in c.fetchall():
            if isinstance(x[0], str):
                picklist.add(x[0].encode("utf-8"))
            elif isinstance(x[0], bytes):
                try:
                    picklist.add(x[0].decode("utf-8"))
                except UnicodeDecodeError:
                    picklist.add(x[0].decode("latin-1"))
            else:
                picklist.add(x[0])
        picklist = list(picklist)
    except Exception as e:
        picklist = []
    finally:
        conn.close()
    return picklist


def get_matched_entries(
        s: str, field_values: List[str], m_theta: float = 0.85, s_theta: float = 0.85
) -> Optional[List[Tuple[str, Tuple[str, str, float, float, int]]]]:
    if not field_values:
        return None

    if isinstance(s, str):
        n_grams = split(s)
    else:
        n_grams = s

    matched = dict()
    for field_value in field_values:
        if not isinstance(field_value, str):
            continue
        fv_tokens = split(field_value)
        sm = difflib.SequenceMatcher(None, n_grams, fv_tokens)
        match = sm.find_longest_match(0, len(n_grams), 0, len(fv_tokens))
        if match.size > 0:
            source_match = get_effective_match_source(
                n_grams, match.a, match.a + match.size
            )
            if source_match:  # and source_match.size > 1
                match_str = field_value[match.b: match.b + match.size]
                source_match_str = s[
                                   source_match.start: source_match.start + source_match.size
                                   ]
                c_match_str = match_str.lower().strip()
                c_source_match_str = source_match_str.lower().strip()
                c_field_value = field_value.lower().strip()
                if c_match_str and not is_common_db_term(c_match_str):  # and not is_number(c_match_str)
                    if (
                            is_stopword(c_match_str)
                            or is_stopword(c_source_match_str)
                            or is_stopword(c_field_value)
                    ):
                        continue
                    if c_source_match_str.endswith(c_match_str + "'s"):
                        match_score = 1.0
                    else:
                        if prefix_match(c_field_value, c_source_match_str):
                            match_score = fuzz.ratio(c_field_value, c_source_match_str) / 100
                        else:
                            match_score = 0
                    if (
                            is_commonword(c_match_str)
                            or is_commonword(c_source_match_str)
                            or is_commonword(c_field_value)
                    ) and match_score < 1:
                        continue
                    s_match_score = match_score
                    if match_score >= m_theta and s_match_score >= s_theta:
                        if field_value.isupper() and match_score * s_match_score < 1:
                            continue
                        matched[match_str] = (
                            field_value,
                            source_match_str,
                            match_score,
                            s_match_score,
                            match.size,
                        )

    if not matched:
        return None
    else:
        return sorted(
            matched.items(),
            key=lambda x: (1e16 * x[1][2] + 1e8 * x[1][3] + x[1][4]),
            reverse=True,
        )


@func_set_timeout(200)
def execute_sql(cursor, sql):
    cursor.execute(sql)

    return cursor.fetchall()


# execute predicted sql with a long time limitation (for buiding content index)
@func_set_timeout(2000)
def execute_sql_long_time_limitation(cursor, sql):
    cursor.execute(sql)

    return cursor.fetchall()


def get_column_contents(column_name, table_name, cursor):
    select_column_sql = "SELECT DISTINCT `{}` FROM `{}` WHERE `{}` IS NOT NULL LIMIT 2;".format(column_name, table_name,
                                                                                                column_name)
    results = execute_sql_long_time_limitation(cursor, select_column_sql)
    column_contents = [str(result[0]).strip() for result in results]
    # remove empty and extremely-long contents
    column_contents = [content for content in column_contents if len(content) != 0 and len(content) <= 25]

    return column_contents


def extract_large_numbers(text):
    number_information = []
    patterns = {
        'thousand': 10 ** 3,
        'million': 10 ** 6,
        'billion': 10 ** 9,
        'trillion': 10 ** 12
    }

    for word, multiplier in patterns.items():
        matches = re.findall(r'(\d+\.?\d*)\s*{}'.format(word), text, flags=re.IGNORECASE)
        for match in matches:
            number = float(match) * multiplier
            number_information.append(match + " " + word + " = " + str(int(number)))

    for phrase, number in {'thousands of': 10 ** 3, 'millions of': 10 ** 6, 'billions of': 10 ** 9,
                           'trillions of': 10 ** 12}.items():
        if phrase in text:
            number_information.append(phrase + " = " + str(int(number)))

    large_number_evidence = ""
    for info in number_information:
        large_number_evidence += info + "; "

    return large_number_evidence.strip()


def remove_table_alias(s):
    try:
        tables_aliases = Parser(s).tables_aliases
    except Exception as e:
        return s

    new_tables_aliases = {}
    for i in range(1, 11):
        if "t{}".format(i) in tables_aliases.keys():
            new_tables_aliases["t{}".format(i)] = tables_aliases["t{}".format(i)]

    tables_aliases = new_tables_aliases
    for k, v in tables_aliases.items():
        # remove AS clauses
        s = s.replace("AS " + k + " ", "")
        # replace table alias with thier original names
        s = s.replace(k, v)

    return s


def remove_similar_comments(names, comments):
    '''
    Remove table (or column) comments that have a high degree of similarity with their names

    Arguments:
        names: a list of table (or column) names
        comments: a list of table (or column) comments

    Returns:
        new_comments: a list of new table (or column) comments
    '''
    new_comments = []
    for name, comment in zip(names, comments):
        if name.replace("_", "").replace(" ", "") == comment.replace("_", "").replace(" ", ""):
            new_comments.append("")
        else:
            new_comments.append(comment)

    return new_comments


def get_cursor_from_path(sqlite_path):
    try:
        if not os.path.exists(sqlite_path):
            print("Openning a new connection %s" % sqlite_path)
        connection = sqlite3.connect(sqlite_path, check_same_thread=False)
    except Exception as e:
        print(sqlite_path)
        raise e
    connection.text_factory = lambda b: b.decode(errors="ignore")
    cursor = connection.cursor()
    return cursor


def str_replace_ignore_case(evidence, schema_item_name):
    evidence = re.sub(re.escape(schema_item_name), schema_item_name, evidence, 0, re.IGNORECASE)

    return evidence


def obtain_n_grams(sequence, max_n):
    '''
    returns all grams of sequence less than or equal to `max_n`
    '''
    tokens = word_tokenize(sequence)
    all_grams = []
    for n in range(1, max_n + 1):
        all_grams.extend([" ".join(gram) for gram in ngrams(tokens, n)])

    return all_grams


def preprocess_evidence(evidence, schema_items):
    if evidence.strip() == "":
        return ""

    evidence = evidence.strip()
    # if evidence does not end with ";", add a ";" char
    if not evidence.endswith(";"):
        evidence += ";"

    # lowercase schema items appeared in the evidence
    for table in schema_items:
        if table["table_name"] in evidence.lower():
            evidence = str_replace_ignore_case(evidence, table["table_name"])

        for column_name in table["column_names"]:
            if column_name in evidence.lower():
                evidence = str_replace_ignore_case(evidence, column_name)

    evidence = evidence.replace("< =", "<=").replace("> =", ">=")

    return evidence


def get_db_schema(db_path, db_comments, db_id):
    if db_id in db_comments:
        db_comment = db_comments[db_id]
    else:
        db_comment = None

    cursor = get_cursor_from_path(db_path)

    # obtain table names
    results = execute_sql(cursor, "SELECT name FROM sqlite_master WHERE type='table';")
    table_names = [result[0].lower() for result in results]

    schema = dict()
    schema["schema_items"] = []
    foreign_keys = []
    # for each table
    for table_name in table_names:
        # skip SQLite system table: sqlite_sequence
        if table_name == "sqlite_sequence":
            continue
        # obtain column names in the current table
        results = execute_sql(cursor, "SELECT name, type, pk FROM PRAGMA_TABLE_INFO('{}')".format(table_name))
        column_names_in_one_table = [result[0].lower() for result in results]
        column_types_in_one_table = [result[1].lower() for result in results]
        pk_indicators_in_one_table = [result[2] for result in results]

        column_contents = []
        for column_name in column_names_in_one_table:
            column_contents.append(get_column_contents(column_name, table_name, cursor))

        # obtain foreign keys in the current table
        results = execute_sql(cursor, "SELECT * FROM pragma_foreign_key_list('{}');".format(table_name))
        for result in results:
            if None not in [result[3], result[2], result[4]]:
                foreign_keys.append([table_name.lower(), result[3].lower(), result[2].lower(), result[4].lower()])

        # obtain comments for each schema item
        if db_comment is not None:
            if table_name in db_comment:  # record comments for tables and columns
                table_comment = db_comment[table_name]["table_comment"]
                column_comments = [db_comment[table_name]["column_comments"][column_name] \
                                       if column_name in db_comment[table_name]["column_comments"] else "" \
                                   for column_name in column_names_in_one_table]
            else:  # current database has comment information, but the current table does not
                table_comment = ""
                column_comments = ["" for _ in column_names_in_one_table]
        else:  # current database has no comment information
            table_comment = ""
            column_comments = ["" for _ in column_names_in_one_table]

        schema["schema_items"].append({
            "table_name": table_name,
            "table_comment": table_comment,
            "column_names": column_names_in_one_table,
            "column_types": column_types_in_one_table,
            "column_comments": column_comments,
            "column_contents": column_contents,
            "pk_indicators": pk_indicators_in_one_table
        })

    schema["foreign_keys"] = foreign_keys

    return schema


def spider_style_dataset(
        dataset_path,
        db_path,
        db_content_index_path,
        source,
        table_json_path,
        use_evidence,
        mode
):
    '''
    Load spider-style dataset

    Arguments:
        dataset_path: directory to load the dataset from
        db_path: directory of databases (used for extracting schema, including tables, columns, column contents, and foreign keys)
        db_content_index_path: directory of database content sparse index
        source: source of examples
        table_json_path: directory to load additional database information (used for extracting comments for tables and columns)
        use_evidence: whether to use the additional evidence in the input sequence
    Returns:
        returned_dataset: prepared dataset
    '''
    returned_dataset = []

    dataset = json.load(open(dataset_path))
    additional_db_info = json.load(open(table_json_path))

    db_comments = dict()
    # record comments for tables and columns
    for db_info in additional_db_info:
        comment_dict = dict()

        column_names = [column_name.lower() for _, column_name in db_info["column_names_original"]]
        table_idx_of_each_column = [t_idx for t_idx, _ in db_info["column_names_original"]]
        column_comments = [column_comment.lower() for _, column_comment in db_info["column_names"]]

        assert len(column_names) == len(column_comments)
        column_comments = remove_similar_comments(column_names, column_comments)

        table_names = [table_name.lower() for table_name in db_info["table_names_original"]]
        table_comments = [table_comment.lower() for table_comment in db_info["table_names"]]

        assert len(table_names) == len(table_comments)
        table_comments = remove_similar_comments(table_names, table_comments)

        # enumerate each table and its columns
        for table_idx, (table_name, table_comment) in enumerate(zip(table_names, table_comments)):
            comment_dict[table_name] = {
                "table_comment": table_comment,
                "column_comments": dict()
            }
            for t_idx, column_name, column_comment in zip(table_idx_of_each_column, column_names, column_comments):
                # record columns in current table
                if t_idx == table_idx:
                    comment_dict[table_name]["column_comments"][column_name] = column_comment

        db_comments[db_info["db_id"]] = comment_dict

    db_ids = set([data["db_id"] for data in dataset])
    db_id2searcher = dict()
    for db_id in db_ids:
        db_id2searcher[db_id] = LuceneSearcher(os.path.join(db_content_index_path, db_id))

    db_id2schema = dict()

    for data in dataset:
        sample = {}
        db_id = data["db_id"]

        sample["db_id"] = db_id
        sample["db_path"] = os.path.join(db_path, db_id, db_id + ".sqlite")

        if db_id in db_id2schema:
            sample["schema"] = db_id2schema[db_id]
        else:
            db_id2schema[db_id] = get_db_schema(sample["db_path"], db_comments, db_id)
            sample["schema"] = db_id2schema[db_id]

        if "spider-syn" in source:
            sample["question"] = data["SpiderSynQuestion"]
            sample["evidence"] = ""
        elif "bird" in source:
            sample["question"] = data["question"]
            evidence = preprocess_evidence(data["evidence"], sample["schema"]["schema_items"])
            sample["evidence"] = evidence
        elif "bank" in source:
            sample["question"] = data["question"]
            sample["evidence"] = extract_large_numbers(data["question"])
        else:
            sample["question"] = data["question"]
            sample["evidence"] = ""

        if "\n" in sample["question"]:
            sample["question"] = sample["question"].replace("\n", " ")
        if "\n" in sample["evidence"]:
            sample["evidence"] = sample["evidence"].replace("\n", " ")

        sample["text"] = sample["evidence"] + " " + sample["question"] \
            if use_evidence and sample["evidence"] != "" else sample["question"]

        if mode in ["train", "dev"]:
            sql = data["SQL"] if source in ["bird-dev", "bird-train"] else data["query"]
            sample["sql"] = remove_table_alias(sqlparse.format(sql, keyword_case="upper", identifier_case="lower"))
        elif mode == "test":
            sample["sql"] = ""

        sample["table_labels"], sample["column_labels"] = [], []
        try:
            sql_tokens = [token.value for token in Parser(sample["sql"].lower()).tokens]
        except Exception as e:
            sql_tokens = sample["sql"].lower().split()

        for table_info in sample["schema"]["schema_items"]:
            if mode in ["train", "dev"]:
                table_name = table_info["table_name"]
                sample["table_labels"].append(1 if table_name in sql_tokens else 0)
                sample["column_labels"].append(
                    [1 if column_name in sql_tokens or table_name + "." + column_name in sql_tokens else 0 \
                     for column_name in table_info["column_names"]])
            elif mode == "test":
                sample["table_labels"].append(0)
                sample["column_labels"].append([0 for _ in range(len(table_info["column_names"]))])

        # coarse-grained matching between the input text and all contents in database
        grams = obtain_n_grams(sample["text"], 4)
        hits = []
        searcher = db_id2searcher[db_id]
        for query in grams:
            hits.extend(searcher.search(query, k=10))

        # hits = searcher.search(sample["text"], k = 50)

        coarse_matched_contents = dict()
        for i in range(len(hits)):
            matched_result = json.loads(hits[i].raw)
            # `tc_name` refers to column names like `table_name.column_name`, e.g., document_drafts.document_id
            tc_name = ".".join(matched_result["id"].split("-**-")[:2])
            if tc_name in coarse_matched_contents.keys():
                if matched_result["contents"] not in coarse_matched_contents[tc_name]:
                    coarse_matched_contents[tc_name].append(matched_result["contents"])
            else:
                coarse_matched_contents[tc_name] = [matched_result["contents"]]

        fine_matched_contents = dict()
        for tc_name, contents in coarse_matched_contents.items():
            # fine-grained matching between the question and coarse matched contents
            fm_contents = get_matched_entries(sample["text"], contents)

            if fm_contents is None:
                continue
            for _match_str, (field_value, _s_match_str, match_score, s_match_score, _match_size,) in fm_contents:
                if match_score < 0.9:
                    continue
                if tc_name in fine_matched_contents.keys():
                    if len(fine_matched_contents[tc_name]) < 25:
                        fine_matched_contents[tc_name].append(field_value.strip())
                else:
                    fine_matched_contents[tc_name] = [field_value.strip()]

        sample["matched_contents"] = fine_matched_contents
        sample["source"] = source

        returned_dataset.append(sample)

    del db_id2searcher

    return returned_dataset


if __name__ == "__main__":
    print("preparing training sets.....")
    print("spider-train")
    spider_train = []
    # Spider training set-1 (7000 + 1658 examples)
    for spider_train_set in ["train_spider.json", "train_others.json"]:
        spider_train.extend(
            spider_style_dataset(
                dataset_path=os.path.join("./data/sft_data_collections/spider/", spider_train_set),
                db_path="./data/sft_data_collections/spider/database",
                db_content_index_path="./data/sft_data_collections/spider/db_contents_index",
                source="spider-train",
                table_json_path="./data/sft_data_collections/spider/tables.json",
                use_evidence=False,
                mode="train"
            )
        )
    with open("./data/sft_spider_train_text2sql.json", "w") as f:
        f.write(json.dumps(spider_train, indent=2, ensure_ascii=False))

    print("BIRD (without evidence) train")
    # BIRD training set (9428 examples)
    bird_train = spider_style_dataset(
        dataset_path="./data/sft_data_collections/bird/train/train.json",
        db_path="./data/sft_data_collections/bird/train/train_databases",
        db_content_index_path="./data/sft_data_collections/bird/train/db_contents_index",
        source="bird-train",
        table_json_path="./data/sft_data_collections/bird/train/train_tables.json",
        use_evidence=False,
        mode="train"
    )
    with open("./data/sft_bird_train_text2sql.json", "w") as f:
        f.write(json.dumps(bird_train, indent=2, ensure_ascii=False))

    print("BIRD (with evidence) train")
    # BIRD training set with evidence (9428 examples)
    bird_with_evidence_train = spider_style_dataset(
        dataset_path="./data/sft_data_collections/bird/train/train.json",
        db_path="./data/sft_data_collections/bird/train/train_databases",
        db_content_index_path="./data/sft_data_collections/bird/train/db_contents_index",
        source="bird-train",
        table_json_path="./data/sft_data_collections/bird/train/train_tables.json",
        use_evidence=True,
        mode="train"
    )
    with open("./data/sft_bird_with_evidence_train_text2sql.json", "w") as f:
        f.write(json.dumps(bird_with_evidence_train, indent=2, ensure_ascii=False))

    print("Bank_Financials train")
    # Bank_Financials train set
    bank_train = spider_style_dataset(
        dataset_path="./data/sft_data_collections/domain_datasets/Bank_Financials_train.json",
        db_path="./data/sft_data_collections/domain_datasets/databases",
        db_content_index_path="./data/sft_data_collections/domain_datasets/db_contents_index",
        source="bank_financials-train",
        table_json_path="./data/sft_data_collections/domain_datasets/tables.json",
        use_evidence=True,
        mode="train"
    )
    with open("./data/sft_bank_financials_train_text2sql.json", "w") as f:
        f.write(json.dumps(bank_train, indent=2, ensure_ascii=False))

    print("Aminer_Simplified train")
    # Aminer_Simplified train set
    aminer_train = spider_style_dataset(
        dataset_path="./data/sft_data_collections/domain_datasets/Aminer_Simplified_train.json",
        db_path="./data/sft_data_collections/domain_datasets/databases",
        db_content_index_path="./data/sft_data_collections/domain_datasets/db_contents_index",
        source="Aminer_Simplified-train",
        table_json_path="./data/sft_data_collections/domain_datasets/tables.json",
        use_evidence=True,
        mode="train"
    )
    with open("./data/sft_aminer_simplified_train_text2sql.json", "w") as f:
        f.write(json.dumps(aminer_train, indent=2, ensure_ascii=False))

    print("Spider + BIRD + Bank_Financials + Aminer_Simplified train set (ALL MERGED)")
    # merge all available training data
    with open("./data/sft_all_merged_train_text2sql.json", "w") as f:
        f.write(json.dumps(spider_train + bird_with_evidence_train + bank_train + aminer_train, indent=2,
                           ensure_ascii=False))

    print("---------------------------------------------------------------------------")
    print("preparing dev sets.....")
    print("spider-dk")
    # Spider-DK development set (535 examples)
    spider_dk = spider_style_dataset(
        dataset_path="./data/sft_data_collections/Spider-DK/Spider-DK.json",
        db_path="./data/sft_data_collections/spider/database",
        db_content_index_path="./data/sft_data_collections/spider/db_contents_index",
        source="spider-dk",
        table_json_path="./data/sft_data_collections/Spider-DK/tables.json",
        use_evidence=False,
        mode="dev"
    )
    with open("./data/sft_spider_dk_text2sql.json", "w") as f:
        f.write(json.dumps(spider_dk, indent=2, ensure_ascii=False))

    print("spider-syn")
    # Spider-Syn development set (1034 examples)
    spider_syn = spider_style_dataset(
        dataset_path="./data/sft_data_collections/Spider-Syn/Spider-Syn/dev.json",
        db_path="./data/sft_data_collections/spider/database",
        db_content_index_path="./data/sft_data_collections/spider/db_contents_index",
        source="spider-syn-dev",
        table_json_path="./data/sft_data_collections/spider/tables.json",
        use_evidence=False,
        mode="dev"
    )
    with open("./data/sft_spider_syn_text2sql.json", "w") as f:
        f.write(json.dumps(spider_syn, indent=2, ensure_ascii=False))

    print("spider-realistic")
    # Spider-Realistic development set (507 examples)
    spider_realistic = spider_style_dataset(
        dataset_path="./data/sft_data_collections/spider-realistic/spider-realistic.json",
        db_path="./data/sft_data_collections/spider/database",
        db_content_index_path="./data/sft_data_collections/spider/db_contents_index",
        source="spider-realistic",
        table_json_path="./data/sft_data_collections/spider/tables.json",
        use_evidence=False,
        mode="dev"
    )
    with open("./data/sft_spider_realistic_text2sql.json", "w") as f:
        f.write(json.dumps(spider_realistic, indent=2, ensure_ascii=False))

    print("DR.spider")
    dr_spider = []
    # Dr.Spider has 17 perturbation test sets
    test_set_names = os.listdir("./data/sft_data_collections/diagnostic-robustness-text-to-sql/data")
    test_set_names.remove("Spider-dev")
    for test_set_name in test_set_names:
        if test_set_name.startswith("DB_"):
            database_file_path = "database_post_perturbation"
            table_file_name = "tables_post_perturbation.json"
        else:
            database_file_path = "databases"
            table_file_name = "tables.json"
        dr_spider.extend(
            spider_style_dataset(
                dataset_path=os.path.join("./data/sft_data_collections/diagnostic-robustness-text-to-sql/data/",
                                          test_set_name, "questions_post_perturbation.json"),
                db_path=os.path.join("./data/sft_data_collections/diagnostic-robustness-text-to-sql/data/",
                                     test_set_name, database_file_path),
                db_content_index_path=os.path.join(
                    "./data/sft_data_collections/diagnostic-robustness-text-to-sql/data/", test_set_name,
                    "db_contents_index"),
                source="dr.spider-{}".format(test_set_name),
                table_json_path=os.path.join("./data/sft_data_collections/diagnostic-robustness-text-to-sql/data/",
                                             test_set_name, table_file_name),
                use_evidence=False,
                mode="dev"
            )
        )
    with open("./data/sft_dr_spider_text2sql.json", "w") as f:
        f.write(json.dumps(dr_spider, indent=2, ensure_ascii=False))

    print("spider-dev")
    # Spider development set (1034 examples)
    spider_dev = spider_style_dataset(
        dataset_path="./data/sft_data_collections/spider/dev.json",
        db_path="./data/sft_data_collections/spider/database",
        db_content_index_path="./data/sft_data_collections/spider/db_contents_index",
        source="spider-dev",
        table_json_path="./data/sft_data_collections/spider/tables.json",
        use_evidence=False,
        mode="dev"
    )
    with open("./data/sft_spider_dev_text2sql.json", "w") as f:
        f.write(json.dumps(spider_dev, indent=2, ensure_ascii=False))

    print("BIRD-dev (without evidence)")
    # BIRD dev set (1534 examples)
    bird_dev = spider_style_dataset(
        dataset_path="./data/sft_data_collections/bird/dev/dev.json",
        db_path="./data/sft_data_collections/bird/dev/dev_databases",
        db_content_index_path="./data/sft_data_collections/bird/dev/db_contents_index",
        source="bird-dev",
        table_json_path="./data/sft_data_collections/bird/dev/dev_tables.json",
        use_evidence=False,
        mode="dev"
    )
    with open("./data/sft_bird_dev_text2sql.json", "w") as f:
        f.write(json.dumps(bird_dev, indent=2, ensure_ascii=False))

    print("BIRD-dev (with evidence)")
    # BIRD dev set (1534 examples)
    bird_with_evidence_dev = spider_style_dataset(
        dataset_path="./data/sft_data_collections/bird/dev/dev.json",
        db_path="./data/sft_data_collections/bird/dev/dev_databases",
        db_content_index_path="./data/sft_data_collections/bird/dev/db_contents_index",
        source="bird-dev",
        table_json_path="./data/sft_data_collections/bird/dev/dev_tables.json",
        use_evidence=True,
        mode="dev"
    )
    with open("./data/sft_bird_with_evidence_dev_text2sql.json", "w") as f:
        f.write(json.dumps(bird_with_evidence_dev, indent=2, ensure_ascii=False))

    print("Bank_Financials dev set")
    # Bank_Financials dev set (92 examples)
    bank_dev = spider_style_dataset(
        dataset_path="./data/sft_data_collections/domain_datasets/Bank_Financials_dev.json",
        db_path="./data/sft_data_collections/domain_datasets/databases",
        db_content_index_path="./data/sft_data_collections/domain_datasets/db_contents_index",
        source="bank_financials-dev",
        table_json_path="./data/sft_data_collections/domain_datasets/tables.json",
        use_evidence=True,
        mode="dev"
    )
    with open("./data/sft_bank_financials_dev_text2sql.json", "w") as f:
        f.write(json.dumps(bank_dev, indent=2, ensure_ascii=False))

    print("Aminer_Simplified dev set")
    # Aminer_Simplified dev set (xxx examples)
    aminer_dev = spider_style_dataset(
        dataset_path="./data/sft_data_collections/domain_datasets/Aminer_Simplified_dev.json",
        db_path="./data/sft_data_collections/domain_datasets/databases",
        db_content_index_path="./data/sft_data_collections/domain_datasets/db_contents_index",
        source="aminer_simplified-dev",
        table_json_path="./data/sft_data_collections/domain_datasets/tables.json",
        use_evidence=True,
        mode="dev"
    )
    with open("./data/sft_aminer_simplified_dev_text2sql.json", "w") as f:
        f.write(json.dumps(aminer_dev, indent=2, ensure_ascii=False))