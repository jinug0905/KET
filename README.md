# Korea Envision Tomorrow Plus - Carbon Neutral Urban Planning Tool  
**기후변화 대응 및 탄소중립 도시 모델 개발 툴**

This project is inspired by the U.S. urban development tool *Envision Tomorrow* and was developed as part of a contract project with Pusan National University. It is a scenario planning tool designed to classify urban development types, identify factors influencing carbon emissions, and analyze the impact of policy decisions. The program enables users to simulate changes in carbon emissions through building type modifications and rooftop greening in Geumjeong-gu, Busan, providing a visual representation of the carbon footprint during urban development.

이 프로젝트는 미국의 도시 개발 툴 *Envision Tomorrow*에서 영감을 받아 부산대학교와의 계약 프로젝트로 개발되었습니다. 도시 개발 유형을 분류하고, 도시의 탄소 배출에 영향을 미치는 요인을 도출하며, 정책 결정의 영향을 분석하기 위한 시나리오 플래닝 툴입니다. 이 프로그램을 통해 부산 금정구의 건물 유형과 옥상 녹화를 수정하여 탄소 배출 변화를 시뮬레이션할 수 있으며, 도시 개발 중 탄소 발자국을 시각적으로 표현합니다.

### Key Features / 주요 기능
- **Carbon Emission Analysis:** Modify building types and rooftop greening to observe changes in carbon emissions across the city.  
  **탄소 배출 분석:** 건물 유형 및 옥상 녹화를 수정하여 도시 전체의 탄소 배출 변화를 관찰할 수 있습니다.
- **Geospatial Data Processing:** Integrated geospatial datasets and performed CRS transformations using GeoPandas.  
  **지리공간 데이터 처리:** GeoPandas를 사용하여 지리공간 데이터를 통합하고 좌표 참조 시스템(CRS)을 변환했습니다.
- **Interactive Visualization:** Built an interactive map with Bokeh to display real-time carbon absorption and emission data, complete with dynamic updates and detailed tooltips for enhanced user interaction.  
  **인터랙티브 시각화:** Bokeh를 사용하여 실시간 탄소 흡수 및 배출 데이터를 보여주는 인터랙티브 지도를 구축했으며, 동적 업데이트와 세부 툴팁을 통해 사용자 상호작용을 강화했습니다.
- **Algorithm Integration:** Applied algorithms from multiple engineering fields, including civil and architectural, to analyze carbon impacts.  
  **알고리즘 통합:** 토목 및 건축 공학을 포함한 여러 공학 분야의 알고리즘을 적용하여 탄소 영향을 분석했습니다.

### Required Libraries / 필요한 라이브러리
- Python 3.9+
- GDAL
- Other libraries in `requirements.txt`  
  **그 외 `requirements.txt`에 있는 라이브러리**

### Project Details / 프로젝트 세부사항
- **Organization:** Pusan National University, College of Engineering  
  **주관:** 부산대학교 공과대학
- **Lead Organizer:** Juchul Jung, Ph.D., Dean of Engineering, Pusan National University  
  **주관자:** 정주철 박사, 부산대학교 공과대학 학장
- **Project Period:** March 2024 – August 2024  
  **프로젝트 기간:** 2024년 3월 – 2024년 8월
- **Sponsor:** Ministry of Environment for sustainable development  
  **후원:** 지속 가능한 개발을 위한 환경부

### Authors / 제작자
- **Developer:** Jinug Lee, M.S. Student in Computer Science and Engineering, Texas A&M University  
  **제작자:** 이진욱, 텍사스 A&M대학교 컴퓨터 공학 석사 과정
- **Contact:** jinug0905@gmail.com  
  **이메일:** jinug0905@gmail.com
