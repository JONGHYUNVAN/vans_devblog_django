"""
VansDevBlog 검색 서비스 샘플 데이터 생성

Nori 한국어 분석기 테스트를 위한 샘플 게시물 데이터를 생성합니다.
"""

import os
import django
from datetime import datetime, timedelta
import random

# Django 설정 초기화
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vans_search_service.settings')
django.setup()

from search.documents import PostDocument

def create_sample_posts():
    """
    Nori 분석기 테스트를 위한 샘플 게시물을 생성합니다.
    
    한국어와 영어가 혼재된 기술 블로그 포스트를 생성하여
    Nori 분석기의 성능을 테스트합니다.
    """
    
    # 샘플 게시물 데이터
    sample_posts = [
        {
            "title": "Django와 Elasticsearch 연동하기",
            "content": """
            Django 웹 프레임워크에서 Elasticsearch를 사용하여 검색 기능을 구현하는 방법을 알아보겠습니다.
            
            먼저 django-elasticsearch-dsl 패키지를 설치해야 합니다. 이 패키지는 Django ORM과 유사한 방식으로 
            Elasticsearch 문서를 정의할 수 있게 해줍니다.
            
            pip install django-elasticsearch-dsl
            
            다음으로 settings.py에서 Elasticsearch 연결을 설정합니다. ELASTICSEARCH_DSL 설정을 통해 
            Elasticsearch 클러스터에 연결할 수 있습니다.
            
            검색 성능을 높이기 위해서는 적절한 분석기 설정이 중요합니다. 특히 한국어 검색의 경우 
            Nori 분석기를 사용하면 형태소 분석을 통해 정확한 검색 결과를 얻을 수 있습니다.
            """,
            "category": "Backend",
            "tags": ["Django", "Elasticsearch", "Python", "검색", "백엔드"],
            "language": "ko"
        },
        {
            "title": "React와 TypeScript로 모던 웹 개발하기",
            "content": """
            React 18과 TypeScript를 사용한 모던 웹 개발 가이드입니다.
            
            React Hooks를 활용하면 함수형 컴포넌트에서도 상태 관리와 생명주기를 쉽게 다룰 수 있습니다.
            useState, useEffect, useContext 등의 기본 Hook들부터 시작해서 
            커스텀 Hook을 만드는 방법까지 알아보겠습니다.
            
            TypeScript를 사용하면 개발 시점에 타입 오류를 잡을 수 있어 더 안정적인 코드를 작성할 수 있습니다.
            interface와 type alias를 적절히 활용하여 컴포넌트의 props와 state를 명확히 정의해보겠습니다.
            
            또한 Next.js 프레임워크를 사용하면 서버사이드 렌더링(SSR)과 정적 사이트 생성(SSG)을 
            쉽게 구현할 수 있습니다.
            """,
            "category": "Frontend",
            "tags": ["React", "TypeScript", "Next.js", "웹개발", "프론트엔드"],
            "language": "ko"
        },
        {
            "title": "Spring Boot와 JPA로 REST API 만들기",
            "content": """
            Spring Boot 프레임워크를 사용하여 RESTful API를 개발하는 방법을 설명합니다.
            
            Spring Boot는 설정을 최소화하고 빠른 개발을 가능하게 하는 Java 기반 프레임워크입니다.
            @RestController, @Service, @Repository 어노테이션을 사용하여 계층별로 코드를 구성할 수 있습니다.
            
            JPA(Java Persistence API)를 사용하면 객체-관계 매핑을 통해 데이터베이스 작업을 
            더 쉽게 처리할 수 있습니다. @Entity, @Id, @Column 등의 어노테이션으로 엔티티를 정의하고
            JpaRepository를 상속받아 CRUD 작업을 간단히 구현할 수 있습니다.
            
            Spring Security를 추가하면 JWT 토큰 기반 인증과 권한 관리도 가능합니다.
            """,
            "category": "Backend",
            "tags": ["Spring Boot", "JPA", "REST API", "Java", "백엔드"],
            "language": "ko"
        },
        {
            "title": "Vue.js 3 Composition API 완벽 가이드",
            "content": """
            Vue.js 3에서 도입된 Composition API의 사용법과 장점을 알아보겠습니다.
            
            Composition API는 기존의 Options API와 달리 로직을 기능별로 구성할 수 있게 해줍니다.
            ref(), reactive(), computed(), watch() 등의 함수를 사용하여 반응형 데이터를 관리할 수 있습니다.
            
            setup() 함수 내에서 컴포넌트의 로직을 정의하고, 템플릿에서 사용할 변수와 함수를 반환합니다.
            이렇게 하면 관련된 로직을 한 곳에 모아 관리할 수 있어 코드의 가독성과 재사용성이 향상됩니다.
            
            TypeScript와 함께 사용하면 타입 안전성까지 확보할 수 있어 더욱 강력한 개발 경험을 제공합니다.
            Vite 번들러를 사용하면 빠른 개발 서버와 효율적인 빌드가 가능합니다.
            """,
            "category": "Frontend",
            "tags": ["Vue.js", "Composition API", "TypeScript", "Vite", "프론트엔드"],
            "language": "ko"
        },
        {
            "title": "Docker와 Kubernetes로 마이크로서비스 배포하기",
            "content": """
            컨테이너 기술을 활용한 마이크로서비스 아키텍처 구축과 배포 방법을 다룹니다.
            
            Docker를 사용하면 애플리케이션을 컨테이너로 패키징하여 어떤 환경에서도 일관된 실행이 가능합니다.
            Dockerfile을 작성하여 이미지를 빌드하고, docker-compose를 사용하여 다중 컨테이너 환경을 구성할 수 있습니다.
            
            Kubernetes는 컨테이너 오케스트레이션 플랫폼으로, 자동 확장, 로드 밸런싱, 서비스 디스커버리 등의 
            기능을 제공합니다. Pod, Service, Deployment, Ingress 등의 리소스를 사용하여 
            애플리케이션을 효율적으로 관리할 수 있습니다.
            
            Helm 차트를 사용하면 Kubernetes 애플리케이션의 패키징과 배포를 더욱 간편하게 할 수 있습니다.
            모니터링을 위해서는 Prometheus와 Grafana를 활용할 수 있습니다.
            """,
            "category": "DevOps",
            "tags": ["Docker", "Kubernetes", "마이크로서비스", "DevOps", "컨테이너"],
            "language": "ko"
        },
        {
            "title": "Node.js와 Express로 백엔드 API 개발하기",
            "content": """
            Node.js 환경에서 Express 프레임워크를 사용한 백엔드 API 개발 가이드입니다.
            
            Express는 가볍고 유연한 웹 프레임워크로, 미들웨어 패턴을 통해 요청과 응답을 처리합니다.
            라우팅, 에러 핸들링, 정적 파일 제공 등의 기능을 간단히 구현할 수 있습니다.
            
            MongoDB와 Mongoose ODM을 사용하면 NoSQL 데이터베이스와의 연동이 쉬워집니다.
            스키마 정의, 유효성 검사, 관계 설정 등을 코드로 관리할 수 있습니다.
            
            JWT(JSON Web Token)를 사용한 인증 시스템과 bcrypt를 활용한 패스워드 암호화도 구현해보겠습니다.
            또한 CORS, 요청 제한, 로깅 등의 보안과 성능 최적화 방법도 알아보겠습니다.
            """,
            "category": "Backend",
            "tags": ["Node.js", "Express", "MongoDB", "JWT", "백엔드"],
            "language": "ko"
        },
        {
            "title": "Python과 FastAPI로 고성능 API 만들기",
            "content": """
            FastAPI 프레임워크를 사용한 고성능 Python 웹 API 개발 방법을 알아보겠습니다.
            
            FastAPI는 현대적인 Python 웹 프레임워크로, 타입 힌트를 기반으로 자동 문서화와 
            유효성 검사를 제공합니다. async/await를 지원하여 높은 성능을 자랑합니다.
            
            Pydantic 모델을 사용하여 요청과 응답 데이터의 구조를 정의할 수 있습니다.
            SQLAlchemy ORM과 함께 사용하면 데이터베이스 작업도 효율적으로 처리할 수 있습니다.
            
            자동으로 생성되는 OpenAPI 문서와 Swagger UI를 통해 API를 쉽게 테스트할 수 있습니다.
            또한 의존성 주입 시스템을 통해 인증, 데이터베이스 연결 등을 깔끔하게 관리할 수 있습니다.
            """,
            "category": "Backend",
            "tags": ["Python", "FastAPI", "SQLAlchemy", "API", "백엔드"],
            "language": "ko"
        },
        {
            "title": "Machine Learning with Python and TensorFlow",
            "content": """
            Python과 TensorFlow를 사용한 머신러닝 모델 개발 가이드입니다.
            
            TensorFlow 2.x는 Eager Execution을 기본으로 하여 더 직관적인 코딩이 가능합니다.
            Keras API를 통해 딥러닝 모델을 쉽게 구성하고 훈련할 수 있습니다.
            
            데이터 전처리를 위해 pandas와 numpy를 활용하고, 시각화를 위해 matplotlib과 seaborn을 사용합니다.
            scikit-learn 라이브러리는 다양한 머신러닝 알고리즘과 평가 지표를 제공합니다.
            
            모델 배포를 위해서는 TensorFlow Serving이나 Flask를 사용할 수 있습니다.
            MLOps를 위한 MLflow나 Kubeflow 같은 도구들도 소개하겠습니다.
            """,
            "category": "AI/ML",
            "tags": ["Machine Learning", "TensorFlow", "Python", "AI", "데이터사이언스"],
            "language": "ko"
        }
    ]
    
    print("📚 샘플 게시물 데이터 생성 중...")
    print("=" * 50)
    
    created_count = 0
    
    for i, post_data in enumerate(sample_posts):
        try:
            # 기본 메타데이터 추가
            post_id = f"sample_post_{i+1:03d}"
            slug = post_data["title"].lower().replace(" ", "-").replace("과", "").replace("를", "").replace("로", "")[:50]
            
            # 읽기 시간 계산 (단어 수 기준)
            word_count = len(post_data["content"].split())
            reading_time = max(1, word_count // 200)
            
            # 랜덤 통계 데이터
            view_count = random.randint(10, 1000)
            like_count = random.randint(0, 50)
            comment_count = random.randint(0, 20)
            
            # 발행일 (지난 30일 내 랜덤)
            days_ago = random.randint(1, 30)
            published_date = datetime.now() - timedelta(days=days_ago)
            
            # PostDocument 생성
            post_doc = PostDocument(
                meta={'id': post_id},
                post_id=post_id,
                title=post_data["title"],
                content=post_data["content"],
                summary=post_data["content"][:200] + "...",
                slug=slug,
                category=post_data["category"],
                tags=post_data["tags"],
                author={
                    'user_id': 'sample_user_001',
                    'username': 'vansdev',
                    'display_name': 'VansDev',
                    'profile_image': 'https://example.com/avatar.jpg'
                },
                published_date=published_date,
                updated_date=published_date,
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                is_published=True,
                language=post_data["language"],
                reading_time=reading_time,
                featured_image='',
                meta_description=post_data["content"][:150],
                search_boost=1.0
            )
            
            # Elasticsearch에 저장
            post_doc.save()
            created_count += 1
            
            print(f"✅ {post_data['title'][:30]}... (ID: {post_id})")
            
        except Exception as e:
            print(f"❌ 게시물 생성 실패: {post_data['title'][:30]}... - {str(e)}")
    
    print("=" * 50)
    print(f"🎉 총 {created_count}개의 샘플 게시물이 생성되었습니다!")
    
    return created_count

if __name__ == "__main__":
    try:
        count = create_sample_posts()
        print(f"\n🔍 이제 검색 API로 테스트해보세요:")
        print("http://localhost:8001/api/v1/search/posts/?query=Django")
        print("http://localhost:8001/api/v1/search/posts/?query=웹개발")
        print("http://localhost:8001/api/v1/search/posts/?category=Backend")
        
    except Exception as e:
        print(f"❌ 샘플 데이터 생성 실패: {str(e)}")
        import traceback
        traceback.print_exc()
