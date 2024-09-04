--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: brand; Type: TABLE; Schema: public; Owner: firmadyne
--

CREATE TABLE public.brand (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.brand OWNER TO firmadyne;

--
-- Name: brand_id_seq; Type: SEQUENCE; Schema: public; Owner: firmadyne
--

CREATE SEQUENCE public.brand_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.brand_id_seq OWNER TO firmadyne;

--
-- Name: brand_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: firmadyne
--

ALTER SEQUENCE public.brand_id_seq OWNED BY public.brand.id;


--
-- Name: image; Type: TABLE; Schema: public; Owner: firmadyne
--

CREATE TABLE public.image (
    id integer NOT NULL,
    filename character varying NOT NULL,
    description character varying,
    brand_id integer DEFAULT 1 NOT NULL,
    hash character varying,
    rootfs_extracted boolean DEFAULT false,
    kernel_extracted boolean DEFAULT false,
    arch character varying,
    kernel_version character varying
);


ALTER TABLE public.image OWNER TO firmadyne;

--
-- Name: image_id_seq; Type: SEQUENCE; Schema: public; Owner: firmadyne
--

CREATE SEQUENCE public.image_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.image_id_seq OWNER TO firmadyne;

--
-- Name: image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: firmadyne
--

ALTER SEQUENCE public.image_id_seq OWNED BY public.image.id;


--
-- Name: object; Type: TABLE; Schema: public; Owner: firmadyne
--

CREATE TABLE public.object (
    id integer NOT NULL,
    hash character varying
);


ALTER TABLE public.object OWNER TO firmadyne;

--
-- Name: object_id_seq; Type: SEQUENCE; Schema: public; Owner: firmadyne
--

CREATE SEQUENCE public.object_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.object_id_seq OWNER TO firmadyne;

--
-- Name: object_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: firmadyne
--

ALTER SEQUENCE public.object_id_seq OWNED BY public.object.id;


--
-- Name: object_to_image; Type: TABLE; Schema: public; Owner: firmadyne
--

CREATE TABLE public.object_to_image (
    id integer NOT NULL,
    oid integer NOT NULL,
    iid integer NOT NULL,
    filename character varying NOT NULL,
    regular_file boolean DEFAULT true,
    permissions integer,
    uid integer,
    gid integer
);


ALTER TABLE public.object_to_image OWNER TO firmadyne;

--
-- Name: object_to_image_id_seq; Type: SEQUENCE; Schema: public; Owner: firmadyne
--

CREATE SEQUENCE public.object_to_image_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.object_to_image_id_seq OWNER TO firmadyne;

--
-- Name: object_to_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: firmadyne
--

ALTER SEQUENCE public.object_to_image_id_seq OWNED BY public.object_to_image.id;


--
-- Name: product; Type: TABLE; Schema: public; Owner: firmadyne
--

CREATE TABLE public.product (
    id integer NOT NULL,
    iid integer NOT NULL,
    url character varying NOT NULL,
    mib_hash character varying,
    mib_url character varying,
    sdk_hash character varying,
    sdk_url character varying,
    product character varying,
    version character varying,
    build character varying,
    date timestamp without time zone,
    mib_filename character varying,
    sdk_filename character varying,
    device_class character varying
);


ALTER TABLE public.product OWNER TO firmadyne;


--
-- Name: product_id_seq; Type: SEQUENCE; Schema: public; Owner: firmadyne
--

CREATE SEQUENCE public.product_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_id_seq OWNER TO firmadyne;

--
-- Name: product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: firmadyne
--

ALTER SEQUENCE public.product_id_seq OWNED BY public.product.id;


--
-- Name: brand id; Type: DEFAULT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.brand ALTER COLUMN id SET DEFAULT nextval('public.brand_id_seq'::regclass);


--
-- Name: image id; Type: DEFAULT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.image ALTER COLUMN id SET DEFAULT nextval('public.image_id_seq'::regclass);


--
-- Name: object id; Type: DEFAULT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.object ALTER COLUMN id SET DEFAULT nextval('public.object_id_seq'::regclass);


--
-- Name: object_to_image id; Type: DEFAULT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.object_to_image ALTER COLUMN id SET DEFAULT nextval('public.object_to_image_id_seq'::regclass);


--
-- Name: product id; Type: DEFAULT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.product ALTER COLUMN id SET DEFAULT nextval('public.product_id_seq'::regclass);


--
-- Name: brand brand_name_key; Type: CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.brand
    ADD CONSTRAINT brand_name_key UNIQUE (name);


--
-- Name: brand brand_pkey; Type: CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.brand
    ADD CONSTRAINT brand_pkey PRIMARY KEY (id);


--
-- Name: image image_pkey; Type: CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.image
    ADD CONSTRAINT image_pkey PRIMARY KEY (id);


--
-- Name: object object_hash_key; Type: CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.object
    ADD CONSTRAINT object_hash_key UNIQUE (hash);


--
-- Name: object object_pkey; Type: CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.object
    ADD CONSTRAINT object_pkey PRIMARY KEY (id);


--
-- Name: object_to_image object_to_image_oid_iid_filename_key; Type: CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.object_to_image
    ADD CONSTRAINT object_to_image_oid_iid_filename_key UNIQUE (oid, iid, filename);


--
-- Name: object_to_image object_to_image_pk; Type: CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.object_to_image
    ADD CONSTRAINT object_to_image_pk PRIMARY KEY (id);


--
-- Name: product product_iid_product_version_build_key; Type: CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_iid_product_version_build_key UNIQUE (iid, product, version, build);


--
-- Name: product product_pkey; Type: CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_pkey PRIMARY KEY (id);


--
-- Name: image uniq_hash; Type: CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.image
    ADD CONSTRAINT uniq_hash UNIQUE (hash);


--
-- Name: idx_object_hash; Type: INDEX; Schema: public; Owner: firmadyne
--

CREATE INDEX idx_object_hash ON public.object USING btree (hash);


--
-- Name: object_to_image_iid_idx; Type: INDEX; Schema: public; Owner: firmadyne
--

CREATE INDEX object_to_image_iid_idx ON public.object_to_image USING btree (iid);


--
-- Name: object_to_image_iid_idx1; Type: INDEX; Schema: public; Owner: firmadyne
--

CREATE INDEX object_to_image_iid_idx1 ON public.object_to_image USING btree (iid);


--
-- Name: object_to_image_oid_idx; Type: INDEX; Schema: public; Owner: firmadyne
--

CREATE INDEX object_to_image_oid_idx ON public.object_to_image USING btree (oid);


--
-- Name: image image_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.image
    ADD CONSTRAINT image_brand_id_fkey FOREIGN KEY (brand_id) REFERENCES public.brand(id) ON DELETE CASCADE;


--
-- Name: object_to_image object_to_image_iid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.object_to_image
    ADD CONSTRAINT object_to_image_iid_fkey FOREIGN KEY (iid) REFERENCES public.image(id) ON DELETE CASCADE;


--
-- Name: object_to_image object_to_image_oid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.object_to_image
    ADD CONSTRAINT object_to_image_oid_fkey FOREIGN KEY (oid) REFERENCES public.object(id) ON DELETE CASCADE;


--
-- Name: product product_iid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: firmadyne
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_iid_fkey FOREIGN KEY (iid) REFERENCES public.image(id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO firmadyne;


--
-- PostgreSQL database dump complete
--
