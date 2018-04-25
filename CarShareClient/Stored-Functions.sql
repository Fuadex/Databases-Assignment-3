DROP FUNCTION IF EXISTS loginchk(emlog VARCHAR, palog VARCHAR);
CREATE OR REPLACE FUNCTION loginchk(IN emlog VARCHAR, IN palog VARCHAR) RETURNS TABLE (nickname VARCHAR(10), nametitle VARCHAR(10), namegiven VARCHAR(100), namefamily VARCHAR(100), address VARCHAR(200), name VARCHAR, since date, subscribed VARCHAR(20), stat_nrofbookings integer) AS
$$
BEGIN
  RETURN QUERY (SELECT member.nickname, member.nametitle, member.namegiven, member.namefamily, member.address, COALESCE(carbay.name, 'None - Click here to add Homebay'), member.since, member.subscribed, member.stat_nrofbookings
                 FROM carsharing.member LEFT OUTER JOIN carsharing.carbay ON (homebay = bayid)
                 WHERE member.email=emlog AND member.password=palog);
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS uph1(naup VARCHAR);
CREATE OR REPLACE FUNCTION uph1(IN naup VARCHAR) RETURNS TABLE (bayID integer) AS
$$
BEGIN
  RETURN QUERY (SELECT carbay.bayID
                 FROM carsharing.carbay
                 WHERE carbay.name = naup);
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS upses(emups VARCHAR);
CREATE OR REPLACE FUNCTION upses(IN emups VARCHAR) RETURNS TABLE (name VARCHAR(80)) AS
$$
BEGIN
  RETURN QUERY (SELECT carbay.name
                 FROM member JOIN carbay on (homebay = bayid)
                 WHERE member.email=emups);
END;
$$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS upses2(emupses VARCHAR);
CREATE OR REPLACE FUNCTION upses2(IN emupses VARCHAR) RETURNS TABLE (stat_nrofbookings int) AS
$$
BEGIN
  RETURN QUERY (SELECT member.stat_nrofbookings
                 FROM member
                 WHERE email=emupses );
END;
$$ LANGUAGE plpgsql;

