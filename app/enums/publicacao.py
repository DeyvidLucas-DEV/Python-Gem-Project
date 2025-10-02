from enum import Enum


class TipoPublicacaoEnum(str, Enum):
    """Enum para tipos de publicação."""
    MATERIA = "materia"
    DISSERTACAO = "dissertacao"
    LIVRO = "livro"
    TESE = "tese"
    CAPITULO_LIVRO = "capitulo_livro"
    POLICY_BRIEF = "policy_brief"
    ARTIGO = "Artigo"