# 한국어 패치 구현 결과

작성일: {{date_and_timezone}}

## 기준과 범위

- 대상·설치 루트: {{target_and_root}}
- 게임·모드 버전, OS·아키텍처: {{build_identity}}
- 공식 기준 소스·대표 파일 해시: {{source_and_hashes}}
- 엔진 구조 확인 근거: {{yaml_control_strings_g1_palette_and_source_evidence}}
- 기존 패치 유무·재사용한 변경: {{existing_patch_or_fresh_implementation}}
- 요청 범위·제외 범위: {{scope}}

## 최종 변경

{{translation_encoding_fonts_objects_ui_and_version_port_changes}}

- 표시용 토큰 번호·인수·충돌 확인: {{unicode_token_contract}}
- 실제 사용 글꼴·크기·기준선·공급자 지원 OS: {{font_provider_contract}}
- 저장·오브젝트 원본·네트워크 경계의 처리: {{compatibility_boundaries}}

## 검증

| 항목 | 수준·결과 | 확인한 범위와 근거 |
|---|---|---|
| 원본 파싱·키·토큰 | {{catalog_result}} | {{catalog_evidence}} |
| 문자 보존·길이·복사 | {{encoding_result}} | {{encoding_evidence}} |
| 글리프·렌더링·UI | {{rendering_result}} | {{rendering_evidence}} |
| 빌드·필수 테스트 | {{build_result}} | {{build_evidence}} |
| 사용자 입력·저장·로드 | {{persistence_result}} | {{persistence_evidence}} |
| 배포 파일·소스 재현 | {{release_result}} | {{release_evidence}} |

미수행·실패한 항목과 사용자가 확인한 화면·버전·수정 전후를 구분해서 기록한다.

## 설치 상태와 산출물

- 실제 교체·추가한 파일: {{installed_files}}
- 실행·언어 선택: {{launch_and_locale}}
- 배포물·수정 소스·재현 절차: {{artifacts}}
- 백업·해시·원복 방법: {{backup_and_restore}}
- 라이선스·필요 런타임: {{notices_and_dependencies}}

## 남은 제한

{{unverified_behavior_and_known_limits}}
