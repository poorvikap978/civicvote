CREATE OR REPLACE FUNCTION update_vote_count()
RETURNS TRIGGER
LANGUAGE plpgsql AS '
BEGIN
    UPDATE candidates
    SET vote_count = vote_count + 1
    WHERE candidate_id = NEW.candidate_id;
    RETURN NEW;
END;
';

DROP TRIGGER
IF
  EXISTS trg_update_vote_count
  ON votes;

  CREATE TRIGGER trg_update_vote_count
  AFTER INSERT
  ON votes
  FOR EACH ROW EXECUTE FUNCTION update_vote_count();


  -- TRIGGER 2: Mark voter as has_voted = TRUE after vote is cast

  CREATE OR REPLACE FUNCTION mark_voter_voted()
  RETURNS TRIGGER
  LANGUAGE plpgsql AS '
BEGIN
    UPDATE voters
    SET has_voted = TRUE
    WHERE voter_id = NEW.voter_id;

    -- Also log to audit
    INSERT INTO audit_log (voter_id, action, status, details)
    VALUES (NEW.voter_id, ''VOTE_CAST'', ''success'',
        ''Vote cast successfully for election_id: '' || NEW.election_id);

    RETURN NEW;
END;
';

  DROP TRIGGER
  IF
    EXISTS trg_mark_voter_voted
    ON votes;

    CREATE TRIGGER trg_mark_voter_voted
    AFTER INSERT
    ON votes
    FOR EACH ROW EXECUTE FUNCTION mark_voter_voted();