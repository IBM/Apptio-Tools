# Contributing to IBM Apptio Tools

Thank you for contributing to IBM Apptio Tools.

This repository contains community-contributed solutions for IBM Apptio products and related integrations, including automation, API scripts, configurations, utilities, and cross-product integrations. Contributions may be made by IBM employees, authorized partners, and members of the broader community.

Please review this document before submitting a contribution.

## 1. Scope of Contributions

Contributions may include:

- **Intra-product solutions**: Automation, API scripts, configurations, or utilities that extend or automate capabilities within an Apptio product
- **Cross-product integrations**: Solutions that move, transform, synchronize, or otherwise integrate data between Apptio products or between Apptio and other systems
- **Product automation and utilities**: Scripts, tools, examples, or supporting utilities that simplify recurring tasks or enable capabilities not readily available through a product's user interface

Solutions may use any appropriate technology, including Python, PowerShell, Bash, REST APIs, Postman, Terraform, SQL, documentation, or other technologies.

### Repository Organization

Product-specific solutions should generally be placed under the applicable product directory.

Cross-product integrations should be placed under the repository's `Integrations/` directory rather than under either the source or target product.

Use descriptive directory and file names. `kebab-case` is recommended for directories and conventional names should be used for files where practical. These naming conventions are recommendations rather than absolute requirements.

## 2. Before Contributing

Before starting work:

1. Review the repository documentation and existing solutions.
2. Review open issues and pull requests to avoid duplicating existing work.
3. For significant enhancements, new solutions, or substantial changes, open an issue first to discuss the proposed contribution.
4. Confirm that the contribution does not contain confidential information, customer-sensitive information, unauthorized IBM intellectual property, or third-party material that cannot legally be redistributed.

## 3. Contribution Process

### Create a Fork or Branch

As the default approach, contributors should fork the repository, create a feature branch in their fork, and submit a pull request from the fork.

Contributors who have write access to the repository may instead create a feature branch directly in the `IBM/Apptio-Tools` repository.

Use a descriptive branch name that identifies the work being performed.

### Implement the Change

Implement the solution according to the requirements in this document.

Contributors should:

- Follow the repository's applicable documentation and naming conventions
- Include a `README.md` for each contributed solution using the standardized solution README template
- Identify prerequisites, dependencies, authentication requirements, compatibility, and known limitations
- Perform reasonable testing and document the results
- Follow the repository's security and intellectual property requirements
- Include the required Apache-2.0 source file header where applicable

### Commit the Change

All commits must include the required Developer Certificate of Origin (DCO) sign-off.

Use `git commit -s` when creating commits, for example:

```bash
git commit -s -m "Add example Cloudability automation"
```

The resulting commit should contain a line similar to:

```text
Signed-off-by: Your Name <your.email@example.com>
```

### Submit a Pull Request

Submit a pull request targeting the repository's `main` branch.

The pull request should:

- Clearly describe the purpose and impact of the change
- Identify the applicable Apptio products
- Identify dependencies and prerequisites
- Describe testing performed
- Identify security considerations
- Identify breaking changes or known limitations
- Confirm the required DCO sign-off
- Use the repository's pull request template when one is provided

Address reviewer feedback and update the pull request as needed.

At least one authorized maintainer must approve the pull request before it can be merged.

Only authorized maintainers should merge pull requests into the protected default branch.

## 4. Solution Documentation

Every contributed solution must include a `README.md` based on the standardized solution README template.

At a minimum, the README should document (**bolded** are the most important):

- **Overview**
- **Supported Products**
- **Solution Details**
- **Prerequisites**
- **Installation/Configuration**
- **Usage**
- **Authentication and Permissions**
- **Dependencies**
- **Testing and Validation**
- **Execution Safety and Recovery**
- Maturity
- **Known Limitations**
- Support and Feedback
- Additional References
- Change History

Sections may be marked `N/A` when they do not apply.

For cross-product integrations, the README should identify the source and target product(s), data direction, APIs used, transformations performed, authentication requirements, dependencies, and compatibility considerations.

## 5. Security and Intellectual Property

Contributors must take reasonable steps to ensure that contributions are safe to publish in a public repository.

### Never Commit

Do not commit:

- Passwords, API keys, access tokens, private keys, certificates containing private material, or other credentials
- Customer-identifiable, customer-confidential, or otherwise sensitive customer information
- IBM internal, restricted, or confidential information that is not authorized for public release
- Confidential business information
- Non-public IBM intellectual property that is not authorized for publication in this repository
- Third-party copyrighted material unless it is appropriately licensed or permission has been obtained

### Security Practices

Where applicable:

- Use environment variables or an approved secrets mechanism instead of embedding credentials in source code
- Avoid exposing credentials in command-line arguments, logs, screenshots, examples, or test data
- Do not disable TLS or certificate validation merely to make a solution work
- Use the minimum permissions necessary for the solution
- Consider the impact of scripts that create, modify, delete, or otherwise affect production resources
- Prefer non-destructive defaults, dry-run or preview capabilities, explicit confirmation for consequential actions, and useful execution summaries where practical
- If a credential or other secret is accidentally exposed, treat it as compromised and rotate or revoke it promptly

Security vulnerabilities should not be reported through public GitHub issues. Follow the repository's security policy for private reporting.

## 6. Dependencies

Contributions must identify significant external dependencies.

Where practical:

- Include dependency manifests or lockfiles
- Pin dependency versions when appropriate
- Document required versions and compatibility
- Avoid introducing known, unaddressed security vulnerabilities
- Disclose known limitations or security concerns associated with dependencies

Automated dependency and vulnerability scanning may be introduced as repository capabilities mature.

## 7. Testing and Validation

Contributors are responsible for performing reasonable validation of their changes.

Testing requirements depend on the nature of the solution. Automated tests are recommended where practical but are not universally required.

Document:

- What was tested
- The environment or product version used for testing
- Any test data or assumptions
- Known limitations
- Any testing that could not be performed

Any automated checks configured as required repository policies must pass before a pull request can be merged.

## 8. Execution Safety

Solutions that execute actions against customer or production environments should be designed with appropriate safety considerations.

Recommended practices include:

- Non-destructive defaults
- Dry-run or preview modes
- Explicit confirmation before consequential operations
- Clear documentation of the actions the solution performs
- Appropriate logging and execution summaries
- Rollback or recovery guidance where practical

These practices are recommendations rather than mandatory requirements for every solution. The appropriate level of safety depends on the solution's purpose and potential impact.

## 9. Maturity

Each solution should identify its maturity.

**Experimental**

Early-stage solution with limited validation. Users should expect changes and should validate the solution carefully before use.

**Validated/Tested**

The solution has been tested and confirmed in a documented environment or set of circumstances.

## 10. Source Code and Licensing

The repository is licensed under the Apache License 2.0.

Contributions must comply with the repository license and applicable third-party licenses.

Source files should include the appropriate Apache-2.0 license header and SPDX identifier where required by the repository's conventions.

Do not add third-party code or content unless its licensing permits redistribution and the applicable license and attribution requirements are satisfied.

## 11. Ownership and Support

Contributors may be credited as the original authors of their solutions, but contributing a solution does not create an obligation to maintain it indefinitely.

Once accepted, solutions are community-maintained. Other contributors may fix, improve, or extend an existing solution.

Solutions are provided as-is. Users are responsible for evaluating a solution's suitability, testing it in their environment, and confirming compatibility with their products and configurations.

Hosting this repository under the IBM GitHub organization does not by itself imply that a solution is an official IBM offering, product feature, supported service, or IBM endorsement.

The Apache License 2.0 terms, including its warranty and liability provisions, apply to contributions.

## 12. Versioning and Change History

Versioning is recommended for solutions that are released, reused, or expected to evolve over time.

**Significant changes should be documented in the solution-specific `CHANGELOG.md`.**

A separate changelog is not required for every small change. Use reasonable judgment based on the significance and expected reuse of the solution.

For changes that substantially alter how a solution is installed, configured, used, or behaves, clearly describe the change in the solution's `CHANGELOG.md` and `README.md` so users can understand what they need to update or adjust.

## 13. Maintainer Review and Approval

Maintainers are responsible for governing the repository and reviewing contributions.

At least one authorized maintainer must formally approve each pull request before it is merged.

Maintainer approval does not mean that the approving maintainer becomes the technical owner or long-term maintainer of the contributed solution.

The repository's `MAINTAINERS.md` identifies authorized maintainers.

The GitHub repository's branch protection or ruleset configuration may impose additional requirements before a pull request can be merged.

## 14. Reporting Issues

Use GitHub Issues to report bugs, request enhancements, or discuss proposed improvements.

When reporting an issue, provide enough information to reproduce or understand the problem, including where appropriate:

- Solution name and version
- Product and product version
- Environment information
- Steps to reproduce
- Expected behavior
- Actual behavior
- Relevant error messages or sanitized logs

Do not include credentials, customer-sensitive information, confidential information, or other restricted content in a public issue.

Security vulnerabilities must be reported privately according to the repository's security policy.

## 15. Disclaimer

Contributions to this repository are provided on an as-is basis.

Solutions are not necessarily official IBM offerings and should not be assumed to be supported, warranted, certified, or endorsed by IBM or the applicable Apptio product team solely because they are hosted in this repository.

Users are responsible for testing solutions, evaluating compatibility, and determining whether a solution is appropriate for their environment.

The repository's Apache License 2.0 governs the applicable warranty and liability terms.

Thank you for contributing to IBM Apptio Tools.
