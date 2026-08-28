---
name: sql-orm-indicator-audit
description: Static and dynamic audit skill for detecting performance bottlenecks, anti-patterns, security risks, and index degradation indicators across raw SQL and ORM queries (JPA, TypeORM, SQLAlchemy, Prisma).
version: 1.0.0
disable-model-invocation: true
---

# SQL & ORM Indicator Audit Skill

Audit database query logic in raw SQL and ORM mapping code for performance bottlenecks, execution-plan regressions, concurrency hazards, and injection vulnerabilities.

## 1. Audit Target Indicators

### Performance & Anti-Patterns

- **N+1 Query Issue:** Iteration loops triggering lazy-loading roundtrips instead of eager joins (`JOIN FETCH`, `selectinload`, `include/relations`, `EntityGraph`).
- **Cartesian Products:** Concurrent multi-collection joins (`MultipleBagFetchException`) or missing `JOIN ON` predicates.
- **Full Table Scans & SARGability Failures:**
  - Predicate wrapping: `WHERE YEAR(col) = ?`, `WHERE LOWER(col) = ?`, `WHERE col + 10 > ?`.
  - Leading wildcards: `LIKE '%pattern'`.
  - Implicit type conversion across mismatched column/parameter types.
- **Unbounded Ingestion:** Unpaginated bulk queries (`LIMIT`/`OFFSET` or cursor pagination omitted) and indiscriminate `SELECT *` projection.

### Concurrency & Lifecycle

- **Extended Transactions:** Network I/O or third-party service calls executed within transaction boundaries (`@Transactional`, `session.begin()`).
- **Pessimistic Locking Deadlocks:** Unordered resource locking via `SELECT FOR UPDATE`.
- **State Drift & Leaks:** Inefficient dirty checking churn and unbounded cascade states (`CascadeType.ALL`, missing `orphanRemoval`).

### Security

- **Injection Candidates:** Dynamic query construction via string formatting, interpolation, or concatenation that bypasses parameter binding.

## 2. Static Analysis: Regex & AST Rules

Regexes are triage heuristics, not security proofs. Report a **candidate** first, then inspect the complete source-to-query path. A non-match is not evidence that a query is safe.

### Regex Detection Patterns

#### `SQL-REG-01` — Dynamic SQL assembly candidate

```regex
(?i)(\bquery\b|\bexecute\b|\bnativeQuery\b)\s*\([^)]*(?:\+|%|\.format\s*\(|f["']|`[^`]*\$\{)
```

This covers common concatenation, `%` formatting, `.format(...)`, f-string, and template-literal forms. Language parsers or taint analysis are required for authoritative injection findings.

#### `SQL-REG-02` — Leading wildcard

```regex
(?i)LIKE\s+['"]%[^'"]+['"]
```

#### `SQL-REG-03` — Non-SARGable expression in predicate

```regex
(?i)WHERE\s+[a-zA-Z0-9_]+\s*\([^)]*\)\s*(=|<|>|<=|>=|LIKE)
```

#### `SQL-REG-04` — Unconstrained query projection

```regex
(?i)\bSELECT\s+\*\s+FROM\b
```

#### `SQL-REG-05` — In-loop repository/ORM fetch

```regex
(?s)(for\s*\([^)]+\)|for\s+[a-zA-Z0-9_]+\s+in\s+[^:]+:|\.forEach\s*\([^)]*\))\s*\{[^}]*\b(repository|em|db|session)\.[a-zA-Z0-9_]+\s*\(
```

### AST Rule Specifications

The following are language-agnostic rule specifications, not executable configuration. Map them to a supported AST or taint-analysis tool before relying on them.

```yaml
ast_rules:
  - id: AST-JPA-001
    name: detect-lazy-collection-traversal-in-loop
    matcher:
      node_type: ForEachStatement | ForStatement | MethodCallExpression
      pattern:
        inside: "for (...) { $ENTITY.get$COLLECTION().forEach(...); }"
        exclude: "JOIN FETCH | @EntityGraph"
    severity: High
    message: "Collection traversal within loop body may cause N+1 queries. Apply JOIN FETCH or EntityGraph when verified."

  - id: AST-ORM-002
    name: detect-io-inside-transaction
    matcher:
      node_type: MethodDeclaration
      pattern:
        annotated_with: "@Transactional | @db.transaction"
        contains:
          node_type: MethodCallExpression
          match: "HttpClient.* | RestTemplate.* | WebClient.* | fetch(*)"
    severity: Critical
    message: "Network I/O inside transaction scope may exhaust connection pools. Confirm transaction ownership and move I/O outside when possible."

  - id: AST-SEC-003
    name: detect-dynamic-sql-concatenation
    matcher:
      node_type: BinaryExpression | TemplateLiteral
      pattern:
        parent_node: "createQuery | createNativeQuery | $db.query"
        contains_operator: "+"
    severity: Critical
    message: "Dynamic SQL assembly detected. Use parameterized queries or prepared statements."
```

## 3. Severity Matrix

| Severity | Criteria | Action Required |
| --- | --- | --- |
| **Critical** | Confirmed SQL injection, network I/O inside transactions, or unindexed mutations on mission-critical paths. | Block deployment; immediate fix. |
| **High** | Verified N+1 execution loops, Cartesian product joins, or unpaginated large-table queries. | Resolve in current sprint. |
| **Medium** | Non-SARGable predicates on indexed columns, `SELECT *` over-fetching, or inefficient eager fetches. | Queue for scheduled refactor. |
| **Low** | Redundant subqueries or minor DTO projection omissions. | Advisory recommendation. |

A regex or AST candidate alone is not a confirmed finding and must not be assigned a Critical or High severity without context.

## 4. Audit Workflow

1. **Static Analysis & Pattern Matching:** Run AST rules and regexes against repository, service, and entity layers. Label results as candidates until verified.
2. **Safe Query Plan Evaluation:** Prefer static inspection or plain `EXPLAIN`. Never run `EXPLAIN ANALYZE` by default: it executes the statement and can trigger writes or side effects. Use it only after explicit approval, in a disposable non-production environment, inside a read-only transaction with a statement timeout. Do not execute DDL or DML as part of this audit.
3. **Remediation Generation:** Provide side-by-side AS-IS and TO-BE code snippets with verification metrics where evidence exists. Do not invent query counts or timing improvements.

## 5. Safety Controls

- The default audit is static and must not connect to or modify a database.
- Never run audit queries against production without explicit authorization; prefer sanitized plans or captured plans.
- Treat all dynamic SQL as untrusted until parameter binding and the complete query path are verified.
- Record unsupported language constructs and unresolved candidates instead of issuing a clean security verdict.

## 6. Output Report Format

````markdown
### [SEVERITY] Summary Title

* **Location:** `path/to/file.ext:line_number`
* **Indicator:** (e.g., AST-JPA-001 / N+1 Query / SARGability Failure)
* **Root Cause:** Explanation of query behavior and database overhead.

* **AS-IS:**
```language
// Problematic code
```

* **TO-BE:**
```language
// Optimized query/ORM code
```

* **Impact:** Measured reduction in query count, execution time, or scan scope; otherwise state that measurement is unavailable.
````
