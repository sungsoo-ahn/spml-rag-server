# Closing Tasks

When done for the day:

1. Query the current date and time
2. In `docs/logs/<today's date>/` write a log file of all you did today
   - Run `ls docs/logs/` and check other days to see the naming convention
   - If `docs/logs/<today's date>/` does not exist, create it
   - Before writing, peek into another day to see the naming convention
   - Format should include hour, minute, and main topic (e.g., `HHMM_main_topic.md`)

3. If you made file or folder structure changes, update `docs/structure.txt`. Even if you didn't try to verify *rough* consistency.

4. For RAG server work:
   - Document any changes to the RAG server architecture or configuration
   - Note any new document types added or extractors created
   - Update statistics if documents were indexed (total count, chunks, etc.)

5. For research/experimental work:
   - Update (or write if non-existing) `docs/research_context.md` with research goals, scope, findings, and current state
   - Ask the user if unclear about research direction
   - DO NOT hallucinate research directions or goals the user did not mention