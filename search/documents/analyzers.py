"""
VansDevBlog Search Service Elasticsearch Analyzers

Elasticsearch 분석기(Analyzer) 설정을 정의합니다.
한국어/영어 다국어 검색을 위한 Nori 분석기를 포함합니다.
"""

from elasticsearch_dsl import analyzer

# =============================================================================
# 분석기 정의
# =============================================================================

# 한국어 분석기 (Nori 토크나이저 사용)
korean_analyzer = analyzer(
    'korean_analyzer',
    tokenizer='nori_tokenizer',
    filter=[
        'lowercase',
        'nori_part_of_speech',
        'nori_readingform',
        'stop'
    ]
)

# 영어 분석기
english_analyzer = analyzer(
    'english_analyzer',
    tokenizer='standard',
    filter=[
        'lowercase',
        'stop',
        'snowball'
    ]
)

# 검색용 분석기
search_analyzer = analyzer(
    'search_analyzer',
    tokenizer='keyword',
    filter=['lowercase']
)

# =============================================================================
# 인덱스 설정 템플릿
# =============================================================================

BASE_INDEX_SETTINGS = {
    # === 기본 인덱스 설정 ===
    'number_of_shards': 1,           # 샤드 수
    'number_of_replicas': 0,         # 복제본 수  
    'max_result_window': 10000,      # 최대 검색 결과 수
    
    # === 텍스트 분석 설정 ===
    'analysis': {
        # --- 분석기 (Analyzers) ---
        'analyzer': {
            # 한국어 텍스트 분석기
            'korean_analyzer': {
                'type': 'custom',
                'tokenizer': 'nori_tokenizer',    # 한국어 형태소 분석
                'filter': [
                    'lowercase',                   # 소문자 변환
                    'nori_part_of_speech',        # 품사 태그 필터
                    'nori_readingform',           # 읽기 형태 변환
                    'stop'                        # 불용어 제거
                ]
            },
            # 영어 텍스트 분석기
            'english_analyzer': {
                'type': 'custom', 
                'tokenizer': 'standard',          # 표준 토크나이저
                'filter': [
                    'lowercase',                   # 소문자 변환
                    'stop',                       # 불용어 제거
                    'snowball'                    # 어간 추출
                ]
            },
            # 검색용 분석기
            'search_analyzer': {
                'type': 'custom',
                'tokenizer': 'keyword',           # 키워드 토크나이저
                'filter': ['lowercase']           # 소문자 변환만
            }
        },
        
        # --- 토크나이저 (Tokenizers) ---
        'tokenizer': {
            # 한국어 형태소 분석 토크나이저
            'nori_tokenizer': {
                'type': 'nori_tokenizer',
                'decompound_mode': 'mixed',       # 복합어 분해 모드
                'user_dictionary_rules': [        # 사용자 정의 사전
                    'Django',                     # 웹 프레임워크
                    'Elasticsearch',              # 검색 엔진
                    'REST API',                   # API 방식
                    'Spring Boot',                # Java 프레임워크
                    'React',                      # 프론트엔드 라이브러리
                    'Vue.js'                      # 프론트엔드 프레임워크
                ]
            }
        },
        
        # --- 필터 (Filters) ---
        'filter': {
            # 한국어 품사 태그 필터
            'nori_part_of_speech': {
                'type': 'nori_part_of_speech',
                'stoptags': [                     # 제외할 품사 태그들
                    'E',    # 어미
                    'IC',   # 감탄사
                    'J',    # 관계언(조사)
                    'MAG',  # 일반 부사
                    'MAJ',  # 접속 부사
                    'MM',   # 관형사
                    'SP',   # 공백
                    'SSC',  # 닫는 괄호
                    'SSO',  # 여는 괄호
                    'SC',   # 구분자
                    'SE',   # 생략 기호
                    'XPN',  # 체언 접두사
                    'XSA',  # 형용사 파생 접미사
                    'XSN',  # 명사 파생 접미사
                    'XSV',  # 동사 파생 접미사
                    'UNA',  # 알 수 없는 문자
                    'NA',   # 분석 불가
                    'VSV'   # 동사
                ]
            },
            # 한국어 읽기 형태 변환 필터
            'nori_readingform': {
                'type': 'nori_readingform'
            },
            # 불용어 제거 필터
            'stop': {
                'type': 'stop',
                'stopwords': ['_korean_', '_english_']  # 한국어/영어 기본 불용어
            }
        }
    }
}

