from datetime import datetime
from typing import Optional, Union

from Bio import Entrez


class PubMedCrawler:
    """PubMed 文献爬取器，封装 Entrez API 的配置与全部检索逻辑。"""

    def __init__(self, email: str, api_key: str):
        """
        初始化爬取器并配置 Entrez 凭证。

        Args:
            email:   用户邮箱，用于标识请求来源。
            api_key: NCBI API 密钥，用于提升请求速率限制。

        Raises:
            RuntimeError: 配置 Entrez 凭证失败时抛出。
        """
        self.email = email
        self.api_key = api_key
        self._configure_entrez()

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _configure_entrez(self) -> None:
        """将实例凭证写入 Bio.Entrez 全局配置。"""
        Entrez.email = self.email
        Entrez.api_key = self.api_key

    @staticmethod
    def _normalize_year_range(
        year_range: Union[None, int, tuple, list],
    ) -> tuple[int, int]:
        """
        规范化年份范围参数。

        支持 None（当前年份）、单个整数（特定年份）或两个整数的元组/列表。

        Args:
            year_range: 原始年份范围输入。

        Returns:
            (start_year, end_year) 标准元组。

        Raises:
            TypeError:  格式不正确时抛出。
            ValueError: 起始年份大于结束年份时抛出。
        """
        current_year = datetime.now().year

        if year_range is None:
            return current_year, current_year

        if isinstance(year_range, int):
            return year_range, year_range

        if isinstance(year_range, (tuple, list)) and len(year_range) == 2:
            start_year, end_year = year_range
            if not isinstance(start_year, int) or not isinstance(end_year, int):
                raise TypeError("year_range must contain integers")
            if start_year > end_year:
                raise ValueError(
                    "year_range start year cannot be greater than end year"
                )
            return start_year, end_year

        raise TypeError(
            "year_range must be an int or a 2-item tuple/list of ints"
        )

    @staticmethod
    def _build_search_term(
        keyword: str,
        year_range: Union[None, int, tuple, list],
    ) -> str:
        """
        组装 PubMed 搜索查询字符串。

        Args:
            keyword:    搜索关键词。
            year_range: 年份范围（会被 _normalize_year_range 处理）。

        Returns:
            完整的 Entrez 搜索查询字符串。
        """
        start_year, end_year = PubMedCrawler._normalize_year_range(year_range)
        return (
            f"({keyword}) AND "
            f'("{start_year}"[Date - Publication] : "{end_year}"[Date - Publication])'
        )

    @staticmethod
    def _extract_article_data(article_record: dict) -> dict:
        """
        从 PubMed 文章记录中提取结构化数据。

        Args:
            article_record: Entrez.read() 返回的单篇文章记录。

        Returns:
            包含 PMID、Title、Abstract、Journal、PublicationDate、Authors、DOI 的字典。
        """
        citation = article_record["MedlineCitation"]
        article = citation["Article"]
        journal = article.get("Journal", {})
        journal_issue = journal.get("JournalIssue", {})
        pub_date = journal_issue.get("PubDate", {})

        # 摘要
        abstract = ""
        if "Abstract" in article and "AbstractText" in article["Abstract"]:
            abstract = " ".join(
                str(item) for item in article["Abstract"]["AbstractText"]
            )

        # 作者列表
        authors: list[str] = []
        for author in article.get("AuthorList", []):
            collective_name = author.get("CollectiveName", "")
            if collective_name:
                authors.append(str(collective_name))
            else:
                full_name = f"{author.get('ForeName', '')} {author.get('LastName', '')}".strip()
                if full_name:
                    authors.append(full_name)

        # DOI
        doi = ""
        for article_id in article_record.get("PubmedData", {}).get("ArticleIdList", []):
            if getattr(article_id, "attributes", {}).get("IdType") == "doi":
                doi = str(article_id)
                break

        return {
            "PMID": str(citation["PMID"]),
            "Title": str(article.get("ArticleTitle", "")),
            "Abstract": abstract,
            "Journal": str(journal.get("Title", "")),
            "PublicationDate": {
                "Year": str(pub_date.get("Year", "")),
                "Month": str(pub_date.get("Month", "")),
                "Day": str(pub_date.get("Day", "")),
            },
            "Authors": authors,
            "DOI": doi,
        }

    # ------------------------------------------------------------------
    # 公开方法
    # ------------------------------------------------------------------

    def search_articles(
        self,
        keyword: str,
        retmax: int = 10,
        year_range: Union[None, int, tuple, list] = None,
        impact_factor_range=None,
    ) -> list[str]:
        """
        搜索 PubMed 文章并返回 PMID 列表。

        注意：如果 retmax 看起来像年份（>=1900）且 year_range 为 None，
        则自动将其视为 year_range。

        Args:
            keyword:            搜索关键词。
            retmax:             最大返回数量，默认 10。
            year_range:         年份范围，支持 None / int / (start, end)。
            impact_factor_range: 影响因子范围（尚未实现）。

        Returns:
            PubMed ID 字符串列表。

        Raises:
            NotImplementedError: 指定了 impact_factor_range 时抛出。
        """
        if isinstance(retmax, int) and retmax >= 1900 and year_range is None:
            year_range = retmax
            retmax = 10

        if impact_factor_range is not None:
            raise NotImplementedError(
                "Impact factor filtering requires an external journal metrics data source."
            )

        term = self._build_search_term(keyword, year_range)
        handle = Entrez.esearch(db="pubmed", term=term, retmax=retmax)
        record = Entrez.read(handle)
        handle.close()
        return record.get("IdList", [])

    def fetch_article(
        self,
        pmid: Union[str, int],
        author: Optional[str] = None,
        publication_year: Optional[int] = None,
    ) -> Optional[dict]:
        """
        获取指定 PMID 的文章详细信息，可按作者或出版年份过滤。

        Args:
            pmid:            PubMed ID。
            author:          作者姓名子串，不匹配时返回 None。
            publication_year: 出版年份，不匹配时返回 None。

        Returns:
            文章数据字典，过滤不通过时返回 None。
        """
        handle = Entrez.efetch(db="pubmed", id=str(pmid), retmode="xml")
        records = Entrez.read(handle)
        handle.close()

        articles = records.get("PubmedArticle", [])
        if not articles:
            return None

        article_data = self._extract_article_data(articles[0])

        # 作者过滤
        if author is not None:
            author_lower = str(author).strip().lower()
            if not any(author_lower in a.lower() for a in article_data["Authors"]):
                return None

        # 年份过滤
        if publication_year is not None:
            if article_data["PublicationDate"]["Year"] != str(publication_year):
                return None

        return article_data

    def fetch_abstract(self, pmid: Union[str, int]) -> str:
        """
        获取指定 PMID 的文章摘要纯文本。

        Args:
            pmid: PubMed ID。

        Returns:
            文章摘要文本。
        """
        handle = Entrez.efetch(
            db="pubmed", id=str(pmid), rettype="abstract", retmode="text"
        )
        abstract = handle.read()
        handle.close()
        return abstract

    # ------------------------------------------------------------------
    # 魔术方法
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"PubMedCrawler(email={self.email!r})"


# ======================================================================
# 向后兼容的模块级函数 —— 内部委托给默认实例
# ======================================================================

_default_crawler: Optional[PubMedCrawler] = None


def _get_default_crawler() -> PubMedCrawler:
    """获取或创建默认爬取器实例。"""
    global _default_crawler
    if _default_crawler is None:
        raise RuntimeError(
            "请先调用 set_email(email, api_key) 或实例化 PubMedCrawler。"
        )
    return _default_crawler


def set_email(email: str, api_key: str) -> int:
    """设置 NCBI Entrez API 的邮箱和 API 密钥（兼容旧接口）。"""
    global _default_crawler
    try:
        _default_crawler = PubMedCrawler(email, api_key)
        return 0
    except Exception:
        return -1


def search_articles(
    keyword: str,
    retmax: int = 10,
    year_range=None,
    impact_factor_range=None,
) -> list[str]:
    """搜索 PubMed 文章并返回 PMID 列表（兼容旧接口）。"""
    return _get_default_crawler().search_articles(
        keyword, retmax=retmax, year_range=year_range,
        impact_factor_range=impact_factor_range,
    )


def fetch_article(pmid, author=None, publication_year=None) -> Optional[dict]:
    """获取指定 PMID 的文章详细信息（兼容旧接口）。"""
    return _get_default_crawler().fetch_article(
        pmid, author=author, publication_year=publication_year,
    )


def fetch_abstract(pmid) -> str:
    """获取指定 PMID 的文章摘要（兼容旧接口）。"""
    return _get_default_crawler().fetch_abstract(pmid)
