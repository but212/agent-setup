# agent-setup

[![skills.sh](https://img.shields.io/badge/skills.sh-agent--setup-black?logo=vercel&logoColor=white)](https://skills.sh/but212/agent-setup)

[English](../README.md) | **한국어** | [설계 철학](PHILOSOPHY.ko.md) | [기술 명세](skills-spec.md)

코딩 에이전트를 위한 운영 규칙과 스킬 계약을 일반 마크다운(Markdown)으로 제공합니다.

> 공기처럼 가벼운 최소주의 워크플로우를 위해.

## 사용 시점

스킬은 강제된 순차 파이프라인이 아닌 독립적인 온디맨드 모달리티(On-demand modality)입니다:

- `/challenge`: 검증되지 않은 가정이나 모호한 범위 -> 인터뷰를 통해 설계 결정 확정.
- `/lean-design`: 상태 머신, 합타입(Sum types), 스키마 -> 구현 전 불가능한 상태를 제거.
- `AGENTS.md`: 상시 운영 헌법 -> 모든 작업에서 TDD를 강제하고 파괴적 작업 차단.
- `/lean-review`: Diff 감사 및 머지 전 검증 -> 구체적인 반례가 뒷받침된 결함만 보고.
- `/crisp`: PR, 커밋 메시지, 장황한 문서 -> 의미 손실 없이 텍스트 압축.

## 저장소 검증 기준

- **계약 중심(Contract-Driven)**: 각 스킬은 프론트매터(Frontmatter)에 역할, 활성화 조건, 파일 수정 권한을 선언합니다.
- **검증 우선(Verification-First)**: `AGENTS.md`는 에이전트가 실행되지 않은 검사를 'Unverified(미검증)'로 보고하고 논리적 추론과 실행 검증을 엄격히 구분하도록 지시합니다.
- **영향 범위 최소화(Minimal Blast Radius)**: `AGENTS.md`는 파괴적인 git 명령과 요청되지 않은 파일 수정을 금지합니다.
- **CI**: Ubuntu, macOS, Windows 환경에서 검증 스크립트와 단위 테스트를 수행합니다.

## 디렉터리 구조 및 계약

- [AGENTS.md](../AGENTS.md) - 우선순위, 안전 가드, TDD, 핸드오프를 규정하는 핵심 운영 헌법.
- skills/*/SKILL.md - 4가지 모달 계약: [`challenge`](../skills/challenge/SKILL.md)(심층 질의), [`crisp`](../skills/crisp/SKILL.md)(텍스트 압축), [`lean-design`](../skills/lean-design/SKILL.md)(타입/불변식), [`lean-review`](../skills/lean-review/SKILL.md)(적대적 감사).
- [docs/skills-spec.md](skills-spec.md) - 아키텍처 명세 및 품질 게이트.
- [docs/PHILOSOPHY.ko.md](PHILOSOPHY.ko.md) / [docs/PHILOSOPHY.md](PHILOSOPHY.md) - Agent Setup의 설계 철학 및 배경.
- [scripts/deploy_agents.py](../scripts/deploy_agents.py) - `AGENTS.md`와 스킬을 `~/.agents`로 복사(디렉터리 참조 방식은 각 도구에 따름).
- [scripts/validate-skills.py](../scripts/validate-skills.py) - 외부 의존성 없는 메타데이터, 계획, 안전 규칙 검증기.
- [.github/workflows/ci.yml](../.github/workflows/ci.yml) - 멀티 OS GitHub Actions 워크플로우.

## 사용법

1. 대상 작업 영역이나 글로벌 에이전트 디렉터리에 저장소를 복사하거나 미러링합니다.
2. 설정을 `~/.agents`에 배포합니다:

   ```sh
   python3 scripts/deploy_agents.py
   ```

   대상 디렉터리를 변경하려면 `AGENT_HOME` 환경 변수를 지정하십시오.

## 검증

저장소 루트에서 검증을 실행합니다:

```sh
python3 scripts/validate-skills.py
python3 -m unittest discover -s tests -v
```

검증기는 스킬 프론트매터, 일자별 계획 경로, 계획 상태 값, `AGENTS.md` 존재 여부, 문서 줄 수 한도(200줄 이내), `AGENTS.md` 및 `skills/`의 ASCII 전용 Markdown 내용을 검사합니다. 테스트 스위트는 원자적 배포 안전성, 저장소 계약, 구조적 불변식을 검증합니다.

## 상태

스킬 명세는 현재 `stable` 상태입니다. 명세의 구조적 품질 게이트를 통과하며, 이는 에이전트의 런타임 행동 자체를 보증하는 것은 아닙니다.

---

참고 및 출처: `challenge`는 [grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me), `lean-review`는 [ponytail-review](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail-review/SKILL.md), `crisp`는 [caveman](https://github.com/JuliusBrussee/caveman)에서 영감을 받았습니다. 상세 내용은 [NOTICE](../NOTICE) 및 [LICENSE](../LICENSE)를 참조하십시오.
