# Refactor Rules

## Safety

* Never change runtime behavior during refactors
* Preserve public interfaces
* Avoid broad rewrites
* Refactor incrementally

## File Splitting

* One responsibility per module
* Avoid giant files
* Prefer cohesive modules
* Avoid generic helper/common modules

## Dependency Management

* Avoid circular imports
* Minimize coupling
* Prefer dependency inversion where useful

## Validation

After every refactor:

* verify imports
* verify references
* verify tests
* verify startup flow
* verify async lifecycle
* verify side effects

## High Risk Areas

Avoid aggressive refactors on:

* app startup
* dependency injection
* async lifecycle
* global state
* websocket management
* schedulers
