-- Create enum type "frequencytype"
CREATE TYPE "frequencytype" AS ENUM ('per', 'this', 'on');
-- Create enum type "untiltype"
CREATE TYPE "untiltype" AS ENUM ('stopped', 'date', 'amount', 'completed');
-- Create enum type "taskeventaround"
CREATE TYPE "taskeventaround" AS ENUM ('today', 'yesterday', 'specifically');
-- Create enum type "taskstatus"
CREATE TYPE "taskstatus" AS ENUM ('ongoing', 'completed', 'paused');
-- Create enum type "frequencyperiod"
CREATE TYPE "frequencyperiod" AS ENUM ('day', 'week', 'month', 'year');
-- Create enum type "iconnameenum"
CREATE TYPE "iconnameenum" AS ENUM ('gymnastics', 'swimming', 'circle', 'circle_outline', 'square', 'square_outline', 'hexagon', 'hexagon_outline', 'work', 'beach', 'favourite', 'people');
-- Create "users" table
CREATE TABLE "users" ("id" serial NOT NULL, "created" timestamp NOT NULL, "email" character varying(100) NOT NULL, "password_hash" character varying(260) NOT NULL, PRIMARY KEY ("id"), CONSTRAINT "users_email_key" UNIQUE ("email"));
-- Create enum type "weekday"
CREATE TYPE "weekday" AS ENUM ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday');
-- Create "categories" table
CREATE TABLE "categories" ("id" serial NOT NULL, "created" timestamp NOT NULL, "user_id" integer NOT NULL, "name" character varying(100) NOT NULL, "description" character varying(100) NOT NULL, "icon_name" "iconnameenum" NOT NULL, "icon_hex_colour" character varying(6) NOT NULL, "parent_category_id" integer NULL, PRIMARY KEY ("id"), CONSTRAINT "unique_user_category_name" UNIQUE ("user_id", "name"), CONSTRAINT "categories_parent_category_id_fkey" FOREIGN KEY ("parent_category_id") REFERENCES "categories" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION, CONSTRAINT "categories_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION);
-- Create "task_frequencies" table
CREATE TABLE "task_frequencies" ("id" serial NOT NULL, "type" "frequencytype" NOT NULL, "period" "frequencyperiod" NULL, "amount" integer NOT NULL, "use_calendar_period" boolean NOT NULL, "once_on_date" date NULL, "once_per_weekday" "weekday" NULL, "once_at_time" time NULL, PRIMARY KEY ("id"));
-- Create "task_untils" table
CREATE TABLE "task_untils" ("id" serial NOT NULL, "type" "untiltype" NOT NULL, "amount" integer NULL, "date" date NULL, PRIMARY KEY ("id"));
-- Create "tasks" table
CREATE TABLE "tasks" ("id" serial NOT NULL, "created" timestamp NOT NULL, "user_id" integer NOT NULL, "category_id" integer NULL, "name" character varying(100) NOT NULL, "description" character varying(100) NOT NULL, "next_event_datetime" timestamp NULL, "frequency_id" integer NOT NULL, "until_id" integer NOT NULL, "status" "taskstatus" NOT NULL, "manually_completed_at" timestamp NULL, PRIMARY KEY ("id"), CONSTRAINT "tasks_frequency_id_key" UNIQUE ("frequency_id"), CONSTRAINT "tasks_until_id_key" UNIQUE ("until_id"), CONSTRAINT "unique_user_task_name" UNIQUE ("user_id", "name"), CONSTRAINT "tasks_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "categories" ("id") ON UPDATE NO ACTION ON DELETE SET NULL, CONSTRAINT "tasks_frequency_id_fkey" FOREIGN KEY ("frequency_id") REFERENCES "task_frequencies" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION, CONSTRAINT "tasks_until_id_fkey" FOREIGN KEY ("until_id") REFERENCES "task_untils" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION, CONSTRAINT "tasks_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION);
-- Create "task_events" table
CREATE TABLE "task_events" ("id" serial NOT NULL, "created" timestamp NOT NULL, "task_id" integer NOT NULL, "around" "taskeventaround" NOT NULL, "at" timestamp NULL, "effective_datetime" timestamp NOT NULL, PRIMARY KEY ("id"), CONSTRAINT "task_events_task_id_fkey" FOREIGN KEY ("task_id") REFERENCES "tasks" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION);
-- Create "task_metrics" table
CREATE TABLE "task_metrics" ("id" serial NOT NULL, "task_id" integer NOT NULL, "name" character varying(100) NOT NULL, "prompt" character varying(100) NOT NULL, "required" boolean NOT NULL, PRIMARY KEY ("id"), CONSTRAINT "unique_task_metric_name" UNIQUE ("task_id", "name"), CONSTRAINT "task_metrics_task_id_fkey" FOREIGN KEY ("task_id") REFERENCES "tasks" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION);
-- Create "task_event_metrics" table
CREATE TABLE "task_event_metrics" ("id" serial NOT NULL, "task_metric_id" integer NOT NULL, "task_event_id" integer NOT NULL, "value" double precision NOT NULL, PRIMARY KEY ("id"), CONSTRAINT "unique_tast_event_metric" UNIQUE ("task_metric_id", "task_event_id"), CONSTRAINT "task_event_metrics_task_event_id_fkey" FOREIGN KEY ("task_event_id") REFERENCES "task_events" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION, CONSTRAINT "task_event_metrics_task_metric_id_fkey" FOREIGN KEY ("task_metric_id") REFERENCES "task_metrics" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION);
-- Create "user_preferences" table
CREATE TABLE "user_preferences" ("id" serial NOT NULL, "name" character varying(100) NOT NULL, "value" boolean NOT NULL, "user_id" integer NOT NULL, PRIMARY KEY ("id"), CONSTRAINT "user_preferences_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION);
