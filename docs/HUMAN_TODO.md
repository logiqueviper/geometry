# Human actions and decisions

The visual refresh and analytic graph work can be used now. The upgraded journal
research is not submission-ready; the gates below remain explicit.

1. **Enable access to the remaining full texts and TPDS author rules.** Crossref
   and general IEEE author policies now work. The ten closest full papers still
   encounter publisher/proxy access barriers; see `reading_access.json` and
   `LITERATURE_MATRIX.md`. Review the destinations saved in environment settings,
   or provide lawfully accessible copies. Publisher access may be needed for
   closed papers. No secret value is requested in chat.
2. **Approve a concrete prospective experiment plan after literature review.**
   Review `docs/PREREGISTRATION.md` and `analysis/experiment_plan.json`. They are
   drafts, not approved preregistrations. Existing seeds 0–29 are historical.
   Literature review must finish first. Approval is required by the supplied workflow's STEP 3 before final-method
   development and held-out runs. The final freeze tag is intentionally absent.
3. **Describe available prototype hardware.** Provide board model, worker count,
   master model, CPU/memory, network ports per node, managed switch/VLAN support,
   budget, and who can operate it. We will adapt the runbook to real equipment.
   No purchases, prices, or physical outcomes are assumed.
4. **Collect and upload raw calibration measurements when the harness is ready.**
   See `hardware/DATA_SCHEMA.md` and `hardware/RUNBOOK.md`. Calibration and
   validation configurations must remain disjoint. Hardware timing cannot be
   simulated to complete the paper.
5. **Supply authorship and submission choices.** Author names, affiliations,
   funding, conflicts, final title, and final venue remain human decisions.
   Confirm review of AI-assisted code, analysis, figures, and text before making
   an author-approval statement. No institutional similarity-check report exists.

Once a relevant prerequisite changes, retry the affected operation and continue
from the recorded state; do not rerun historical measurements to replace them
with more favorable cases.

The Python/LaTeX workflow is tested. A Docker recipe is included; its build
validation status is recorded in `results/docker-verification.json`. The presence
of a Dockerfile alone does not establish a verified container.
