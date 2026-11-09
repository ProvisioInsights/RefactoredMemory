# RM field catalog version 1

**Status:** Published source contract with opt-in tagged assertion validation in this branch; not deployed or universally activated on existing peers. The focused UI and remaining FC acceptance remain separate.

The packaged [catalog](../refactoredmemory/contracts/fields-v1.json) is the machine-readable source for these definitions. [Client obligations and wire examples](RM-CLIENT-CONTRACT.md) define their use. `memory_schema.field_catalog` publishes the catalog, tag schema and digest. A changed semantic definition requires a new supported contract revision, not an unannounced edit to published v1.

## Coverage and meaning

The starter has 52 definitions: five identity/display fields, three contact fields, eleven reported-profile fields covering sixteen observed property names, seven reported-date fields and twenty-six relationships. The observed families contained 695 profile-property, 473 contact-point and 253 reported-date assertions at the inspected frontier. Counts are assertions, not distinct people or confirmations. This is not a complete census of fields buried in raw legacy text.

Name and type are required for typed record creation; all other starter fields are optional. Name means a sourced display name, not a proven legal identity. Types, fields, relationship predicates and knowledge categories stay distinct. Multiple contacts and sourced profile/date claims coexist. The existing functional alias predicate stores one sourced list; competing lists remain alternatives, never an automatic union.

## Identity, contacts and reported properties

| Field ID | Label | Applies to | Native storage | Cardinality |
| --- | --- | --- | --- | --- |
| `identity.type` | Type | person, organization, project, location, occurrence, topic, offering, item, observation | `rm:canonical-type` | functional |
| `identity.name` | Name | person, organization, project, location, occurrence, topic, offering, item, observation | `name` | functional |
| `identity.aliases` | Aliases | person, organization, project, location, occurrence, topic, offering, item, observation | `alias` | functional |
| `identity.description` | Description | person, organization, project, location, occurrence, topic, offering, item, observation | `description` | functional |
| `identity.status` | Source-reported status | person, organization, project, location, occurrence, topic, offering, item, observation | `status` | functional |
| `contact.email` | Email | person, organization | `rm:contact-point (kind=email)` | multi-valued |
| `contact.phone` | Phone | person, organization | `rm:contact-point (kind=phone)` | multi-valued |
| `contact.url` | Web or profile URL | person, organization, project, offering, location, item | `rm:contact-point (kind=url)` | multi-valued |
| `profile.location` | Reported location | person, organization, project, location, occurrence, topic, offering, item, observation | `rm:profile-property (property=location)` | multi-valued |
| `profile.organization` | Reported organization | person, organization, project | `rm:profile-property (property=org)` | multi-valued |
| `profile.role` | Reported role | person, organization | `rm:profile-property (property=role)` | multi-valued |
| `profile.headquarters` | Reported headquarters | organization | `rm:profile-property (property=headquarters)` | multi-valued |
| `profile.preferred_channel` | Preferred contact channel | person, organization | `rm:profile-property (property=preferred-channel)` | multi-valued |
| `profile.relationship_to_owner` | Relationship to owner | person, organization | `rm:profile-property (property=john-relationship)` | multi-valued |
| `profile.relationship_origin` | Relationship origin | person, organization, project | `rm:profile-property (property=relationship-origin)` | multi-valued |
| `profile.contact_status` | Source-reported contact status | person, organization | `rm:profile-property (property=source-contact-status)` | multi-valued |
| `profile.website_reference` | Website reference or research note | person, organization, project, location, occurrence, topic, offering, item, observation | `rm:profile-property (property=website-reference)` | multi-valued |
| `profile.x_reference` | X reference or research note | person, organization, project, location, occurrence, topic, offering, item, observation | `rm:profile-property (property=x-reference)` | multi-valued |
| `profile.instagram_reference` | Instagram reference or research note | person, organization, project, location, occurrence, topic, offering, item, observation | `rm:profile-property (property=instagram-reference)` | multi-valued |
| `date.start` | Reported start date | person, organization, project, location, occurrence, topic, offering, item, observation | `rm:reported-date (property=start-date)` | multi-valued |
| `date.end` | Reported end date | person, organization, project, location, occurrence, topic, offering, item, observation | `rm:reported-date (property=end-date)` | multi-valued |
| `date.founded` | Reported founding date | organization, project, offering | `rm:reported-date (property=founded)` | multi-valued |
| `date.launched` | Reported launch date | organization, project, offering, item | `rm:reported-date (property=launched)` | multi-valued |
| `date.last_contacted` | Reported last contact | person, organization | `rm:reported-date (property=last-contacted)` | multi-valued |
| `date.source_verified` | Source-reported verification date | person, organization, project, location, occurrence, topic, offering, item, observation | `rm:reported-date (property=verified-date)` | multi-valued |
| `date.reported` | Reported date | person, organization, project, location, occurrence, topic, offering, item, observation | `rm:reported-date (property=date)` | multi-valued |

## Observed profile-name mappings

Mappings preserve the captured property key and its temporal/source qualifications. They do not silently rewrite history, establish current validity, resolve an identity or convert a reported role/organization into a confirmed employment edge. Research-reference notes remain text even when they say no URL was found. A confirmed, syntactically valid contact URL is a different field.

| Canonical field | Existing property names accepted/read |
| --- | --- |
| `profile.location` | `location`, `current-location` |
| `profile.organization` | `org`, `employer-current`, `employer-historical` |
| `profile.role` | `role`, `role-current`, `role-historical` |
| `profile.headquarters` | `headquarters` |
| `profile.preferred_channel` | `preferred-channel` |
| `profile.relationship_to_owner` | `john-relationship` |
| `profile.relationship_origin` | `relationship-origin` |
| `profile.contact_status` | `source-contact-status` |
| `profile.website_reference` | `website-reference` |
| `profile.x_reference` | `x-reference` |
| `profile.instagram_reference` | `instagram-reference` |

## Relationship definitions

Relationships have known target identities, an existing registered category/cardinality, their own sources and explicit validity. Unresolved endpoints remain observations. Required start context can be explicitly unknown; do not invent a day for a month/year source. For `invests-in`, amount is explicit null or `{value, currency}`, and status is one of proposed, discussed, committed, completed, declined, withdrawn or unknown. A proposed/discussed claim must not be presented as completed funding.

| Predicate | From types | To types | Category | Cardinality | Required context |
| --- | --- | --- | --- | --- | --- |
| `employed-by` | person | organization | employment | multi-valued | valid_from |
| `member-of` | person, organization | organization | affiliation | multi-valued | None beyond ordinary operation evidence/time |
| `part-of` | occurrence, project, observation | occurrence, project, observation | structural | functional | None beyond ordinary operation evidence/time |
| `contained-in` | location | location | geography | functional | None beyond ordinary operation evidence/time |
| `has-type` | person, organization, project, location, occurrence, topic, offering, item, observation | topic | taxonomy | multi-valued | None beyond ordinary operation evidence/time |
| `operated-by` | location | organization | structural | multi-valued | None beyond ordinary operation evidence/time |
| `based-in` | person, organization | location | geography | functional | None beyond ordinary operation evidence/time |
| `occurred-at` | occurrence | location | occurrence | functional | None beyond ordinary operation evidence/time |
| `participant-in` | person, organization | occurrence, project | occurrence | multi-valued | None beyond ordinary operation evidence/time |
| `connects` | person, organization | person, organization | network | multi-valued | None beyond ordinary operation evidence/time |
| `owns` | person, organization | item, offering, organization | commerce | multi-valued | None beyond ordinary operation evidence/time |
| `offered-by` | offering, occurrence | organization | commerce | functional | None beyond ordinary operation evidence/time |
| `sold-by` | item, offering, occurrence | organization | commerce | functional | None beyond ordinary operation evidence/time |
| `purchased` | person | item, offering, occurrence | commerce | multi-valued | None beyond ordinary operation evidence/time |
| `customer-of` | person, organization | organization | customer | multi-valued | None beyond ordinary operation evidence/time |
| `founder-of` | person | organization | employment | multi-valued | valid_from |
| `acquired-by` | organization | organization | structural | functional | valid_from |
| `invests-in` | person, organization | organization | capital | multi-valued | amount, investment_status |
| `about` | person, organization, project, location, occurrence, topic, offering, item, observation | topic, project | taxonomy | multi-valued | None beyond ordinary operation evidence/time |
| `parent-of` | person | person | personal | multi-valued | None beyond ordinary operation evidence/time |
| `spouse-of` | person | person | personal | multi-valued | None beyond ordinary operation evidence/time |
| `sibling-of` | person | person | personal | multi-valued | None beyond ordinary operation evidence/time |
| `estranged-from` | person | person | personal | multi-valued | None beyond ordinary operation evidence/time |
| `introduced-by` | person | person | network | multi-valued | None beyond ordinary operation evidence/time |
| `created` | person, organization | item, offering | creation | multi-valued | None beyond ordinary operation evidence/time |
| `mentions` | observation | person, organization, project, location, occurrence, topic, offering, item, observation | taxonomy | multi-valued | None beyond ordinary operation evidence/time |

## Missing states and display

Not recorded is read-only absence in the selected authorized view; never write a placeholder. Explicit sourced unknown and not-applicable use a null mapped payload plus their v1 tag state. These states do not assert that the source is correct or reviewed. Withheld/unavailable/conflicted/partial coverage remain separate conditions. Unknown and N/A are always visible meaningful values, even when empty optional fields are hidden. Required missing fields stay visible.

Reported date values use real calendar year/month/day and matching `precision`; legacy `calendar_period` is a read mapping, while tagged new values use `date`. This source-reported value never automatically sets the assertion world interval. World validity keeps the existing day/aware-timestamp formats: explicit null end is unknown, omitted end is ongoing only when the tag explicitly declares ongoing. Preserve original source text and uncertainty.

## Version and compatibility

Applicability for new substantive values uses the deterministic resulting atomic-group classification, including same-group type actions and owner preference. Type establishment/resolution is allowed for an unresolved identity when the declared target is supported. Withdrawing an existing field/relationship does not require its old type to remain applicable; reinstatement does. Clients must keep classification-repair and withdrawal controls usable instead of hiding them solely because the current type is ambiguous or changed.

The tag schema is packaged alongside the catalog. Core checks apply to explicitly tagged v1 assertions and prevent a successor from discarding a governed field declaration. Untagged legacy data remains under the existing knowledge profile; publication is not universal activation. Upgrade and qualify both peers before admitting v1 on a deployed store. Old clients must not treat legacy acceptance as v1 validation.

Catalog changes are operator-controlled code changes, not model-generated data. App templates reuse the discovered definitions and typed controls, with theme/layout/visibility remaining presentation. Consumer record archive and permanent erasure are not enabled by this catalog. See the client contract for safe CRUD and failure behavior.
