DROP VIEW
IF
  EXISTS live_results;

  CREATE VIEW live_results AS
  SELECT
    e.election_id
    , e.title AS election_title
    , c.candidate_id
    , c.full_name AS candidate_name
    , c.party
    , c.party_symbol
    , c.vote_count
    , CASE
      WHEN SUM(c2.vote_count) OVER (
        PARTITION BY e.election_id
      ) = 0
      THEN 0
      ELSE
        ROUND(
          c.vote_count * 100.0 / NULLIF(
            SUM(c2.vote_count) OVER (
              PARTITION BY e.election_id
            )
            , 0
          )
          , 2
        )
    END AS vote_percentage
  FROM
    candidates c
    JOIN elections e
  ON c.election_id = e.election_id
  JOIN candidates c2
  ON c2.election_id = e.election_id
  GROUP BY
    e.election_id
    , e.title
    , c.candidate_id
    , c.full_name
    , c.party
    , c.party_symbol
    , c.vote_count
  ORDER BY
    e.election_id
    , c.vote_count DESC;


  -- VIEW 2: Voter turnout summary per election
  DROP VIEW
  IF
    EXISTS voter_turnout;

    CREATE VIEW voter_turnout AS
    SELECT
      e.election_id
      , e.title AS election_title
      , e.status
      , con.name AS constituency_name
      , con.total_registered_voters
      , COUNT(v.vote_id) AS votes_cast
      , CASE
        WHEN con.total_registered_voters = 0 THEN 0
        ELSE
          ROUND(
            COUNT(v.vote_id) * 100.0 / con.total_registered_voters
            , 2
          )
      END AS turnout_percentage
    FROM
      elections e
      LEFT JOIN votes v
    ON e.election_id = v.election_id
    LEFT JOIN constituencies con
    ON e.constituency_id = con.constituency_id
    GROUP BY
      e.election_id
      , e.title
      , e.status
      , con.name
      , con.total_registered_voters
    ORDER BY
      e.election_id;


    -- STORED PROCEDURE: cast_vote with full verification and ROLLBACK
    CREATE OR REPLACE PROCEDURE cast_vote(
      p_voter_card_no VARCHAR
      , p_aadhaar_no VARCHAR
      , p_candidate_id INT
      , p_election_id INT
    )
    LANGUAGE plpgsql AS '
DECLARE
    v_voter_id INT;
    v_has_voted BOOLEAN;
    v_is_verified BOOLEAN;
    v_election_status VARCHAR;
    v_already_voted INT;
BEGIN
    -- Step 1: Verify voter identity (simulated biometric check)
    SELECT voter_id, has_voted, is_verified
    INTO v_voter_id, v_has_voted, v_is_verified
    FROM voters
    WHERE voter_card_no = p_voter_card_no AND aadhaar_no = p_aadhaar_no;

    IF v_voter_id IS NULL THEN
        INSERT INTO audit_log (action, status, details)
        VALUES (''VOTE_ATTEMPT'', ''failed'', ''Invalid voter credentials: '' || p_voter_card_no);
        RAISE EXCEPTION ''Invalid voter ID or Aadhaar number. Verification failed.'';
    END IF;

    -- Step 2: Check if already voted
    IF v_has_voted THEN
        INSERT INTO audit_log (voter_id, action, status, details)
        VALUES (v_voter_id, ''DUPLICATE_VOTE_ATTEMPT'', ''blocked'', ''Voter already cast vote in this election'');
        RAISE EXCEPTION ''You have already voted. Duplicate voting is not allowed.'';
    END IF;

    -- Step 3: Check election is active
    SELECT status INTO v_election_status
    FROM elections WHERE election_id = p_election_id;

    IF v_election_status != ''active'' THEN
        RAISE EXCEPTION ''Election is not currently active.'';
    END IF;

    -- Step 4: Double-check votes table for duplicate
    SELECT COUNT(*) INTO v_already_voted
    FROM votes WHERE voter_id = v_voter_id AND election_id = p_election_id;

    IF v_already_voted > 0 THEN
        RAISE EXCEPTION ''Duplicate vote detected at database level.'';
    END IF;

    -- Step 5: Cast the vote
    INSERT INTO votes (voter_id, candidate_id, election_id)
    VALUES (v_voter_id, p_candidate_id, p_election_id);

    RAISE NOTICE ''Vote cast successfully for voter_id: %'', v_voter_id;

EXCEPTION
    WHEN OTHERS THEN
        RAISE;
END;
';