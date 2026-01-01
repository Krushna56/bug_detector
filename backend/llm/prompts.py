"""
Prompt templates for LLM interactions
Centralized location for all prompts used in the security agent
"""

# Vulnerability Analysis
VULNERABILITY_ANALYSIS_PROMPT = """
Analyze the following security vulnerability:

**File**: {file_path}
**Vulnerability Type**: {vulnerability_type}
**Severity**: {severity}

**Code Snippet**:
```
{code_snippet}
```

Please provide:
1. A detailed explanation of the vulnerability
2. The potential impact and risk (rate 1-10)
3. Attack scenarios that could exploit this
4. Specific recommendations to fix it
5. Best practices to prevent similar issues

Format your response clearly with sections.
"""

# Patch Generation
PATCH_GENERATION_PROMPT = """
Generate a secure code fix for the following vulnerability:

**File**: {file_path}
**Vulnerability**: {vulnerability_description}

**Current Code**:
```
{code_snippet}
```

Please provide:
1. The fixed/secure version of the code
2. A clear explanation of what was changed and why
3. Any additional security considerations

Format the fixed code in a code block.
"""

# Vulnerability Prioritization
PRIORITIZATION_PROMPT = """
You are analyzing multiple security findings. Prioritize them based on:
- Severity level
- Exploitability
- Business impact
- Ease of remediation

**Context**: {context}

**Findings**:
{findings}

Provide a prioritized list with:
1. Priority level (Critical/High/Medium/Low)
2. Reasoning for the priority
3. Recommended action timeline

Focus on the most critical issues first.
"""

# Explanation Generation
EXPLANATION_PROMPT = """
Explain the following security finding in clear, non-technical terms:

**Finding**: {finding_message}
**Rule**: {rule_id}
**Severity**: {severity}

Provide:
1. What this vulnerability means
2. Why it's a security concern
3. Real-world example of how it could be exploited
4. Simple steps to fix it

Make it understandable for developers who may not be security experts.
"""

# False Positive Detection
FALSE_POSITIVE_PROMPT = """
Analyze if this security finding is a false positive:

**Rule**: {rule_id}
**Message**: {message}
**Code Context**:
```
{code_snippet}
```

**Surrounding Code**:
```
{context}
```

Determine:
1. Is this a true vulnerability or false positive?
2. Confidence level (0-100%)
3. Reasoning for your assessment
4. If false positive, why the scanner flagged it

Be conservative - when in doubt, treat it as a real vulnerability.
"""

# Security Best Practices
BEST_PRACTICES_PROMPT = """
Based on the following code review findings, suggest security best practices:

**Language/Framework**: {language}
**Findings Summary**:
{findings_summary}

Provide:
1. Top 5 security best practices for this codebase
2. Specific code patterns to avoid
3. Recommended security libraries/tools
4. Code review checklist items

Focus on actionable, practical advice.
"""

# Threat Modeling
THREAT_MODEL_PROMPT = """
Perform threat modeling for the following component:

**Component**: {component_name}
**Description**: {description}
**Code**:
```
{code}
```

Identify:
1. Potential threat actors
2. Attack vectors
3. Assets at risk
4. Security controls needed
5. Mitigation strategies

Use STRIDE methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege).
"""

# Code Security Review
CODE_REVIEW_PROMPT = """
Perform a security-focused code review:

**File**: {file_path}
**Code**:
```
{code}
```

Review for:
1. Input validation issues
2. Authentication/authorization flaws
3. Data exposure risks
4. Injection vulnerabilities
5. Cryptographic weaknesses
6. Error handling problems

Provide specific line numbers and recommendations.
"""
