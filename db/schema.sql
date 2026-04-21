DROP TABLE
IF
  EXISTS audit_log CASCADE;
  DROP TABLE
  IF
    EXISTS votes CASCADE;
    DROP TABLE
    IF
      EXISTS candidates CASCADE;
      DROP TABLE
      IF
        EXISTS voters CASCADE;
        DROP TABLE
        IF
          EXISTS elections CASCADE;
          DROP TABLE
          IF
            EXISTS constituencies CASCADE;


            CREATE TABLE constituencies (
              constituency_id SERIAL PRIMARY KEY
              , name VARCHAR(150) NOT NULL
              , district VARCHAR(100)
              , total_registered_voters INT DEFAULT 0
            );


            CREATE TABLE elections (
              election_id SERIAL PRIMARY KEY
              , title VARCHAR(200) NOT NULL
              , description TEXT
              , constituency_id INT REFERENCES constituencies(constituency_id)
              , start_date DATE NOT NULL
              , end_date DATE NOT NULL
              , status VARCHAR(20) CHECK (status IN ('upcoming', 'active', 'completed')) DEFAULT 'upcoming'
              , created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE voters (
              voter_id SERIAL PRIMARY KEY
              , full_name VARCHAR(150) NOT NULL
              , voter_card_no VARCHAR(20) UNIQUE NOT NULL
              , aadhaar_no VARCHAR(12) UNIQUE NOT NULL
              , date_of_birth DATE NOT NULL
              , constituency_id INT REFERENCES constituencies(constituency_id)
              , has_voted BOOLEAN DEFAULT FALSE
              , is_verified BOOLEAN DEFAULT FALSE
              , registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE candidates (
              candidate_id SERIAL PRIMARY KEY
              , full_name VARCHAR(150) NOT NULL
              , party VARCHAR(100) NOT NULL
              , party_symbol VARCHAR(50)
              , election_id INT NOT NULL REFERENCES elections(election_id)
              ON DELETE CASCADE
              , constituency_id INT REFERENCES constituencies(constituency_id)
              , vote_count INT DEFAULT 0
              , manifesto TEXT
            );


            CREATE TABLE votes (
              vote_id SERIAL PRIMARY KEY
              , voter_id INT NOT NULL REFERENCES voters(voter_id)
              , candidate_id INT NOT NULL REFERENCES candidates(candidate_id)
              , election_id INT NOT NULL REFERENCES elections(election_id)
              , voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
              , UNIQUE (voter_id, election_id)
            );


            CREATE TABLE audit_log (
              log_id SERIAL PRIMARY KEY
              , voter_id INT REFERENCES voters(voter_id)
              , action VARCHAR(100) NOT NULL
              , status VARCHAR(20) CHECK (status IN ('success', 'failed', 'blocked'))
              , details TEXT
              , logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );


            INSERT INTO
              constituencies (name, district, total_registered_voters)
            VALUES
              ('Anna Nagar', 'Chennai', 5000)
              , ('T. Nagar', 'Chennai', 4500)
              , ('Velachery', 'Chennai', 4800);

            INSERT INTO
              elections (
                title
                , description
                , constituency_id
                , start_date
                , end_date
                , status
              )
            VALUES
              (
                'Chennai Municipal Elections 2026'
                , 'Municipal body elections for ward representatives'
                , 1
                , '2026-04-01'
                , '2026-04-30'
                , 'active'
              )
              , (
                'Student Council Elections 2026'
                , 'College student council representative election'
                , 2
                , '2026-04-01'
                , '2026-04-30'
                , 'active'
              );

            INSERT INTO
              candidates (
                full_name
                , party
                , party_symbol
                , election_id
                , constituency_id
              )
            VALUES
              ('Rasha Kumar', 'Democratic Party', 'Lotus', 1, 1)
              , ('Priya Sharma', 'Progressive Alliance', 'Star', 1, 1)
              , ('Arjun Mehta', 'Citizens Front', 'Hand', 1, 1)
              , ('Kavitha Rajan', 'People Power', 'Torch', 2, 2)
              , ('Suresh Babu', 'Youth Wing', 'Lion', 2, 2);