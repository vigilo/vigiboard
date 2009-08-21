--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: event_history; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE event_history (
    idhistory integer NOT NULL,
    type_action character varying(27) NOT NULL,
    idevent integer NOT NULL,
    value text,
    text text,
    "timestamp" timestamp without time zone,
    username text
);


ALTER TABLE public.event_history OWNER TO vigiboard;

--
-- Name: event_history_idhistory_seq; Type: SEQUENCE; Schema: public; Owner: vigiboard
--

CREATE SEQUENCE event_history_idhistory_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.event_history_idhistory_seq OWNER TO vigiboard;

--
-- Name: event_history_idhistory_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigiboard
--

ALTER SEQUENCE event_history_idhistory_seq OWNED BY event_history.idhistory;


--
-- Name: events; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE events (
    idevent integer NOT NULL,
    hostname text NOT NULL,
    servicename text,
    severity integer NOT NULL,
    status character varying(12) DEFAULT 'None'::character varying NOT NULL,
    active boolean,
    "timestamp" timestamp without time zone,
    output text NOT NULL,
    timestamp_active timestamp without time zone,
    trouble_ticket text,
    occurence integer,
    impact integer,
    rawstate character varying(8)
);


ALTER TABLE public.events OWNER TO vigiboard;

--
-- Name: events_idevent_seq; Type: SEQUENCE; Schema: public; Owner: vigiboard
--

CREATE SEQUENCE events_idevent_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.events_idevent_seq OWNER TO vigiboard;

--
-- Name: events_idevent_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigiboard
--

ALTER SEQUENCE events_idevent_seq OWNED BY events.idevent;


--
-- Name: graph; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE graph (
    name text NOT NULL,
    template text NOT NULL,
    vlabel text NOT NULL
);


ALTER TABLE public.graph OWNER TO vigiboard;

--
-- Name: graphgroups; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE graphgroups (
    name text NOT NULL,
    parent integer
);


ALTER TABLE public.graphgroups OWNER TO vigiboard;

--
-- Name: graphtogroups; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE graphtogroups (
    graphname text NOT NULL,
    groupname text NOT NULL
);


ALTER TABLE public.graphtogroups OWNER TO vigiboard;

--
-- Name: grouppermissions; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE grouppermissions (
    groupname text NOT NULL,
    idpermission integer NOT NULL
);


ALTER TABLE public.grouppermissions OWNER TO vigiboard;

--
-- Name: groups; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE groups (
    name text NOT NULL,
    parent text
);


ALTER TABLE public.groups OWNER TO vigiboard;

--
-- Name: host; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE host (
    name text NOT NULL,
    checkhostcmd text NOT NULL,
    community text NOT NULL,
    fqhn text NOT NULL,
    hosttpl text NOT NULL,
    mainip text NOT NULL,
    port integer NOT NULL,
    snmpoidsperpdu integer,
    snmpversion text
);


ALTER TABLE public.host OWNER TO vigiboard;

--
-- Name: hostgroups; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE hostgroups (
    hostname text NOT NULL,
    groupname text NOT NULL
);


ALTER TABLE public.hostgroups OWNER TO vigiboard;

--
-- Name: perfdatasource; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE perfdatasource (
    hostname text NOT NULL,
    servicename text NOT NULL,
    graphname text NOT NULL,
    type text NOT NULL,
    label text,
    factor double precision NOT NULL
);


ALTER TABLE public.perfdatasource OWNER TO vigiboard;

--
-- Name: service; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE service (
    name text NOT NULL,
    type text NOT NULL,
    command text NOT NULL
);


ALTER TABLE public.service OWNER TO vigiboard;

--
-- Name: servicegroups; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE servicegroups (
    servicename text NOT NULL,
    groupname text NOT NULL
);


ALTER TABLE public.servicegroups OWNER TO vigiboard;

--
-- Name: servicehautniveau; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE servicehautniveau (
    servicename text NOT NULL,
    servicename_dep text NOT NULL
);


ALTER TABLE public.servicehautniveau OWNER TO vigiboard;

--
-- Name: servicetopo; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE servicetopo (
    servicename text NOT NULL,
    function text NOT NULL
);


ALTER TABLE public.servicetopo OWNER TO vigiboard;

--
-- Name: state; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE state (
    idstat integer NOT NULL,
    hostname text NOT NULL,
    servicename text,
    ip text,
    "timestamp" timestamp without time zone,
    statename character varying(8) DEFAULT 'OK'::character varying NOT NULL,
    type character varying(4) DEFAULT 'SOFT'::character varying NOT NULL,
    attempt integer NOT NULL,
    message text
);


ALTER TABLE public.state OWNER TO vigiboard;

--
-- Name: state_idstat_seq; Type: SEQUENCE; Schema: public; Owner: vigiboard
--

CREATE SEQUENCE state_idstat_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.state_idstat_seq OWNER TO vigiboard;

--
-- Name: state_idstat_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigiboard
--

ALTER SEQUENCE state_idstat_seq OWNED BY state.idstat;


--
-- Name: tg_group; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE tg_group (
    group_id integer NOT NULL,
    group_name character varying(16) NOT NULL,
    display_name character varying(255),
    created timestamp without time zone
);


ALTER TABLE public.tg_group OWNER TO vigiboard;

--
-- Name: tg_group_group_id_seq; Type: SEQUENCE; Schema: public; Owner: vigiboard
--

CREATE SEQUENCE tg_group_group_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.tg_group_group_id_seq OWNER TO vigiboard;

--
-- Name: tg_group_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigiboard
--

ALTER SEQUENCE tg_group_group_id_seq OWNED BY tg_group.group_id;


--
-- Name: tg_group_permission; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE tg_group_permission (
    group_id integer,
    permission_id integer
);


ALTER TABLE public.tg_group_permission OWNER TO vigiboard;

--
-- Name: tg_permission; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE tg_permission (
    permission_id integer NOT NULL,
    permission_name character varying(16) NOT NULL,
    description character varying(255)
);


ALTER TABLE public.tg_permission OWNER TO vigiboard;

--
-- Name: tg_permission_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: vigiboard
--

CREATE SEQUENCE tg_permission_permission_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.tg_permission_permission_id_seq OWNER TO vigiboard;

--
-- Name: tg_permission_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigiboard
--

ALTER SEQUENCE tg_permission_permission_id_seq OWNED BY tg_permission.permission_id;


--
-- Name: tg_user; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE tg_user (
    user_id integer NOT NULL,
    user_name character varying(16) NOT NULL,
    email_address character varying(255) NOT NULL,
    display_name character varying(255),
    password character varying(80),
    created timestamp without time zone
);


ALTER TABLE public.tg_user OWNER TO vigiboard;

--
-- Name: tg_user_group; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE tg_user_group (
    user_id integer,
    group_id integer
);


ALTER TABLE public.tg_user_group OWNER TO vigiboard;

--
-- Name: tg_user_user_id_seq; Type: SEQUENCE; Schema: public; Owner: vigiboard
--

CREATE SEQUENCE tg_user_user_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.tg_user_user_id_seq OWNER TO vigiboard;

--
-- Name: tg_user_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigiboard
--

ALTER SEQUENCE tg_user_user_id_seq OWNED BY tg_user.user_id;


--
-- Name: version; Type: TABLE; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE TABLE version (
    name text NOT NULL,
    version text NOT NULL
);


ALTER TABLE public.version OWNER TO vigiboard;

--
-- Name: idhistory; Type: DEFAULT; Schema: public; Owner: vigiboard
--

ALTER TABLE event_history ALTER COLUMN idhistory SET DEFAULT nextval('event_history_idhistory_seq'::regclass);


--
-- Name: idevent; Type: DEFAULT; Schema: public; Owner: vigiboard
--

ALTER TABLE events ALTER COLUMN idevent SET DEFAULT nextval('events_idevent_seq'::regclass);


--
-- Name: idstat; Type: DEFAULT; Schema: public; Owner: vigiboard
--

ALTER TABLE state ALTER COLUMN idstat SET DEFAULT nextval('state_idstat_seq'::regclass);


--
-- Name: group_id; Type: DEFAULT; Schema: public; Owner: vigiboard
--

ALTER TABLE tg_group ALTER COLUMN group_id SET DEFAULT nextval('tg_group_group_id_seq'::regclass);


--
-- Name: permission_id; Type: DEFAULT; Schema: public; Owner: vigiboard
--

ALTER TABLE tg_permission ALTER COLUMN permission_id SET DEFAULT nextval('tg_permission_permission_id_seq'::regclass);


--
-- Name: user_id; Type: DEFAULT; Schema: public; Owner: vigiboard
--

ALTER TABLE tg_user ALTER COLUMN user_id SET DEFAULT nextval('tg_user_user_id_seq'::regclass);


--
-- Name: event_history_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY event_history
    ADD CONSTRAINT event_history_pkey PRIMARY KEY (idhistory);


--
-- Name: events_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY events
    ADD CONSTRAINT events_pkey PRIMARY KEY (idevent);


--
-- Name: graph_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY graph
    ADD CONSTRAINT graph_pkey PRIMARY KEY (name);


--
-- Name: graphgroups_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY graphgroups
    ADD CONSTRAINT graphgroups_pkey PRIMARY KEY (name);


--
-- Name: graphtogroups_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY graphtogroups
    ADD CONSTRAINT graphtogroups_pkey PRIMARY KEY (graphname, groupname);


--
-- Name: grouppermissions_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY grouppermissions
    ADD CONSTRAINT grouppermissions_pkey PRIMARY KEY (groupname, idpermission);


--
-- Name: groups_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (name);


--
-- Name: host_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY host
    ADD CONSTRAINT host_pkey PRIMARY KEY (name);


--
-- Name: hostgroups_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY hostgroups
    ADD CONSTRAINT hostgroups_pkey PRIMARY KEY (hostname, groupname);


--
-- Name: perfdatasource_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY perfdatasource
    ADD CONSTRAINT perfdatasource_pkey PRIMARY KEY (hostname, servicename);


--
-- Name: service_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY service
    ADD CONSTRAINT service_pkey PRIMARY KEY (name);


--
-- Name: servicegroups_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY servicegroups
    ADD CONSTRAINT servicegroups_pkey PRIMARY KEY (servicename, groupname);


--
-- Name: servicehautniveau_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY servicehautniveau
    ADD CONSTRAINT servicehautniveau_pkey PRIMARY KEY (servicename, servicename_dep);


--
-- Name: servicetopo_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY servicetopo
    ADD CONSTRAINT servicetopo_pkey PRIMARY KEY (servicename);


--
-- Name: state_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY state
    ADD CONSTRAINT state_pkey PRIMARY KEY (idstat);


--
-- Name: tg_group_group_name_key; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY tg_group
    ADD CONSTRAINT tg_group_group_name_key UNIQUE (group_name);


--
-- Name: tg_group_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY tg_group
    ADD CONSTRAINT tg_group_pkey PRIMARY KEY (group_id);


--
-- Name: tg_permission_permission_name_key; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY tg_permission
    ADD CONSTRAINT tg_permission_permission_name_key UNIQUE (permission_name);


--
-- Name: tg_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY tg_permission
    ADD CONSTRAINT tg_permission_pkey PRIMARY KEY (permission_id);


--
-- Name: tg_user_email_address_key; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY tg_user
    ADD CONSTRAINT tg_user_email_address_key UNIQUE (email_address);


--
-- Name: tg_user_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY tg_user
    ADD CONSTRAINT tg_user_pkey PRIMARY KEY (user_id);


--
-- Name: tg_user_user_name_key; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY tg_user
    ADD CONSTRAINT tg_user_user_name_key UNIQUE (user_name);


--
-- Name: version_pkey; Type: CONSTRAINT; Schema: public; Owner: vigiboard; Tablespace: 
--

ALTER TABLE ONLY version
    ADD CONSTRAINT version_pkey PRIMARY KEY (name);


--
-- Name: ix_event_history_idevent; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_event_history_idevent ON event_history USING btree (idevent);


--
-- Name: ix_events_hostname; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_events_hostname ON events USING btree (hostname);


--
-- Name: ix_events_servicename; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_events_servicename ON events USING btree (servicename);


--
-- Name: ix_groups_parent; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_groups_parent ON groups USING btree (parent);


--
-- Name: ix_host_name; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_host_name ON host USING btree (name);


--
-- Name: ix_hostgroups_groupname; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_hostgroups_groupname ON hostgroups USING btree (groupname);


--
-- Name: ix_perfdatasource_graphname; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_perfdatasource_graphname ON perfdatasource USING btree (graphname);


--
-- Name: ix_perfdatasource_servicename; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_perfdatasource_servicename ON perfdatasource USING btree (servicename);


--
-- Name: ix_service_name; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_service_name ON service USING btree (name);


--
-- Name: ix_servicegroups_groupname; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_servicegroups_groupname ON servicegroups USING btree (groupname);


--
-- Name: ix_servicehautniveau_servicename_dep; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_servicehautniveau_servicename_dep ON servicehautniveau USING btree (servicename_dep);


--
-- Name: ix_state_hostname; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_state_hostname ON state USING btree (hostname);


--
-- Name: ix_state_servicename; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_state_servicename ON state USING btree (servicename);


--
-- Name: ix_version_name; Type: INDEX; Schema: public; Owner: vigiboard; Tablespace: 
--

CREATE INDEX ix_version_name ON version USING btree (name);


--
-- Name: event_history_idevent_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY event_history
    ADD CONSTRAINT event_history_idevent_fkey FOREIGN KEY (idevent) REFERENCES events(idevent);


--
-- Name: events_hostname_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY events
    ADD CONSTRAINT events_hostname_fkey FOREIGN KEY (hostname) REFERENCES host(name);


--
-- Name: events_servicename_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY events
    ADD CONSTRAINT events_servicename_fkey FOREIGN KEY (servicename) REFERENCES service(name);


--
-- Name: graphtogroups_graphname_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY graphtogroups
    ADD CONSTRAINT graphtogroups_graphname_fkey FOREIGN KEY (graphname) REFERENCES graph(name);


--
-- Name: graphtogroups_groupname_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY graphtogroups
    ADD CONSTRAINT graphtogroups_groupname_fkey FOREIGN KEY (groupname) REFERENCES graphgroups(name);


--
-- Name: grouppermissions_groupname_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY grouppermissions
    ADD CONSTRAINT grouppermissions_groupname_fkey FOREIGN KEY (groupname) REFERENCES groups(name);


--
-- Name: hostgroups_groupname_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY hostgroups
    ADD CONSTRAINT hostgroups_groupname_fkey FOREIGN KEY (groupname) REFERENCES groups(name);


--
-- Name: hostgroups_hostname_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY hostgroups
    ADD CONSTRAINT hostgroups_hostname_fkey FOREIGN KEY (hostname) REFERENCES host(name);


--
-- Name: perfdatasource_graphname_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY perfdatasource
    ADD CONSTRAINT perfdatasource_graphname_fkey FOREIGN KEY (graphname) REFERENCES graph(name);


--
-- Name: perfdatasource_hostname_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY perfdatasource
    ADD CONSTRAINT perfdatasource_hostname_fkey FOREIGN KEY (hostname) REFERENCES host(name);


--
-- Name: perfdatasource_servicename_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY perfdatasource
    ADD CONSTRAINT perfdatasource_servicename_fkey FOREIGN KEY (servicename) REFERENCES service(name);


--
-- Name: servicegroups_groupname_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY servicegroups
    ADD CONSTRAINT servicegroups_groupname_fkey FOREIGN KEY (groupname) REFERENCES groups(name);


--
-- Name: servicegroups_servicename_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY servicegroups
    ADD CONSTRAINT servicegroups_servicename_fkey FOREIGN KEY (servicename) REFERENCES service(name);


--
-- Name: servicehautniveau_servicename_dep_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY servicehautniveau
    ADD CONSTRAINT servicehautniveau_servicename_dep_fkey FOREIGN KEY (servicename_dep) REFERENCES service(name);


--
-- Name: servicehautniveau_servicename_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY servicehautniveau
    ADD CONSTRAINT servicehautniveau_servicename_fkey FOREIGN KEY (servicename) REFERENCES service(name);


--
-- Name: servicetopo_servicename_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY servicetopo
    ADD CONSTRAINT servicetopo_servicename_fkey FOREIGN KEY (servicename) REFERENCES service(name);


--
-- Name: state_hostname_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY state
    ADD CONSTRAINT state_hostname_fkey FOREIGN KEY (hostname) REFERENCES host(name);


--
-- Name: state_servicename_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY state
    ADD CONSTRAINT state_servicename_fkey FOREIGN KEY (servicename) REFERENCES service(name);


--
-- Name: tg_group_permission_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY tg_group_permission
    ADD CONSTRAINT tg_group_permission_group_id_fkey FOREIGN KEY (group_id) REFERENCES tg_group(group_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: tg_group_permission_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY tg_group_permission
    ADD CONSTRAINT tg_group_permission_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES tg_permission(permission_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: tg_user_group_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY tg_user_group
    ADD CONSTRAINT tg_user_group_group_id_fkey FOREIGN KEY (group_id) REFERENCES tg_group(group_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: tg_user_group_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigiboard
--

ALTER TABLE ONLY tg_user_group
    ADD CONSTRAINT tg_user_group_user_id_fkey FOREIGN KEY (user_id) REFERENCES tg_user(user_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

