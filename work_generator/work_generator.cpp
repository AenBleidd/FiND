#include <unistd.h>
#include <cstdlib>
#include <sstream>
#include <string.h>
#include <cstring>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <sys/stat.h>

#include "boinc/svn_version.h"
#include "boinc/sched_util.h"
#include "boinc/error_numbers.h"
#include "boinc/backend_lib.h"
#include "boinc/boinc_db.h"
#include "sql.h"

const char* template_path = "templates/";
const char* app_name = "vina";
const char* in_template_file = "vina_wu.xml";
const char* out_template = "templates/vina_result.xml";
char *sql_config_file;

DB_APP app;
char *in_template;

int start_time;
int seqno;

int Count(const std::string & str, const std::string & obj) {
	int n = 0;
	std::string::size_type pos = 0;
	while ((pos = obj.find(str, pos)) != std::string::npos) {
		n++;
		pos += str.size();
	}
	return n;
}

bool fileExists(const std::string& filename) {
	struct stat buf;
	if (stat(filename.c_str(), &buf) != -1) {
		return true;
	}
	return false;
}

int createFile(string path, string data) {
	if (!fileExists(path.c_str())) {
		// file doesn't exist
		ofstream myfile(path.c_str());
		if (myfile.is_open()) {
			myfile << data;
			myfile.close();
			return 0;
		} else {
			fprintf(stderr, "Can't create input in downloads: %d\n", 1);
			exit(1);
			return 1;
		}
	} else {
		return 0;
	}
}

int make_job(struct jobstruct job) {
	DB_APP app;
	DB_WORKUNIT wu;
	char* wu_template;
	const char *infiles[3];
	char *path;
	char additional_xml[512];

	log_messages.printf(MSG_DEBUG, "Making files\n");
	// write input file in the download directory
	//
	infiles[0] = job.nameligand;
	infiles[1] = job.namereceptor;
	infiles[2] = job.confname;

	char path_ligand[1024];
	char path_receptor[1024];
	char path_conf[1024];

	int retval;

	config.download_path(job.nameligand, path_ligand);
	retval = createFile(path_ligand, job.pdbligand);
	if (retval) {
		fprintf(stderr, "error making input data\n");
		exit(1);
	}

	config.download_path(job.namereceptor, path_receptor);
	retval = createFile(path_receptor, job.pdbreceptor);
	if (retval) {
		fprintf(stderr, "error making input data\n");
		exit(1);
	}

	config.download_path(job.confname, path_conf);
	retval = createFile(path_conf, job.pdbconf);
	if (retval) {
		fprintf(stderr, "error making input data\n");
		exit(1);
	}

	log_messages.printf(MSG_DEBUG, "Done making files\n");

	wu.clear();     // zeroes all fields

	if (!strlen(wu.name)) {
		/*sprintf(wu.name, "%s_%d_%f-%s-%s-%s-%s-%s-", app_name, getpid(),
		 dtime(), job.idreceptor, job.namereceptor, job.idligand,
		 job.nameligand, job.experiment);*/
		sprintf(wu.name, "%s_%s_%s_%s", app_name, job.idligand, job.idreceptor,
				job.experiment);
	}

	char buff[256];
	sprintf(buff, "where name='%s'", app_name);
	retval = app.lookup(buff);
	if (retval) {
		fprintf(stderr, "create_work: app not found\n");
		exit(1);
	}

	wu.appid = app.id;
	wu.id = 0;
	wu.min_quorum = 1;
	wu.target_nresults = 1;
	wu.max_error_results = 1;
	wu.max_total_results = 5;
	wu.max_success_results = 1;
	wu.rsc_disk_bound = 150000;
	wu.rsc_bandwidth_bound = 0.0;

	int count = Count("between atoms:", job.pdbligand);
	double credit = 1.0 + double(count) * 0.2895;
	if (credit > 25) {
		credit = 25;
	}

	//sprintf(additional_xml, "<credit>%f</credit>\n", credit);

	sprintf(additional_xml,
			"<credit>%f</credit>\n<command_line>--ligand ligand --receptor receptor --config conf --rligand %s --rreceptor %s --cpu 1</command_line>", credit,
			job.nameligand, job.namereceptor);

	log_messages.printf(MSG_DEBUG, "Start create_work()\n");
	create_work(wu, in_template, "templates/vina_result.xml",
			"../templates/vina_result.xml", infiles, 3, config, NULL,
			additional_xml);

	log_messages.printf(MSG_DEBUG, "Done create_work()\n");

	return 0;
}

int Connector::connectDB() {
	connect = mysql_init(NULL); // Initialise the instance
	/* This If is irrelevant and you don't need to show it. I kept it in for Fault Testing.*/
	if (!connect) /* If instance didn't initialize say so and exit with fault.*/
	{
		cout << "MySQL Initialization Failed" << "\n";
		fprintf(stderr, "MySQL Initialization Failed");
		return 1;
	}
	/* Now we will actually connect to the specific database.*/

	mysql_real_connect(connect, creds.host.c_str(), creds.usr.c_str(), creds.pwd.c_str(), creds.base.c_str(), 0, NULL,
			0);

	/* Following if statements are unneeded too, but it's worth it to show on your
	 first app, so that if your database is empty or the query didn't return anything it
	 will at least let you know that the connection to the mysql server was established. */

	if (connect) {
		printf("Connection Succeeded\n");
	} else {
		printf("Connection Failed!\n");
		cout << "Connection Failed!" << "\n";
	}
	fprintf(stderr, "Logged in\n");
	return 0;
}

int Connector::disconnectDB() {
	mysql_close(connect); // dropping the connection
	fprintf(stderr, "Logged out\n");
	return 0;
}

int Connector::getAllTasks() {

	unsigned int numberOfJobs = 0;
	unsigned int *numrows = &numberOfJobs;
	MYSQL_RES *res_set; /* Create a pointer to recieve the return value.*/
	MYSQL_ROW row; /* Assign variable for rows. */

	string a =
			"SELECT tasks.idreceptor, receptors.name, receptors.pdb, receptors.conf_name, receptors.conf, tasks.idligand, ligands.name, ligands.pdb, tasks.experiment from tasks, receptors, ligands WHERE tasks.status = 0 and receptors.idreceptors = tasks.idreceptor and ligands.idligands = tasks.idligand LIMIT 0,1000";

	string b = ";";
	string sql = a + b;

	mysql_query(connect, sql.c_str());
	/* Send a query to the database. */
	//unsigned int i = 0; /* Create a counter for the rows */
	res_set = mysql_store_result(connect); /* Receive the result and store it in res_set */
	*numrows = mysql_num_rows(res_set); /* Create the count to print all rows */

	log_messages.printf(MSG_DEBUG, "Making %d jobs\n", *numrows);

	if (*numrows > 0) {
		fprintf(stderr, "adding tasks\n");
		unsigned int n;
		for (n = 0; n < *numrows; n++) {
			struct jobstruct job;
			row = mysql_fetch_row(res_set);
			job.idreceptor = row[0];
			job.namereceptor = row[1];
			job.pdbreceptor = row[2];
			job.confname = row[3];
			job.pdbconf = row[4];
			job.idligand = row[5];
			job.nameligand = row[6];
			job.pdbligand = row[7];
			job.experiment = row[8];
			//printf("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n",row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]); /* Print the row data */

			int retval = make_job(job);

			if (retval) {
				log_messages.printf(MSG_CRITICAL, "can't make job: %s\n",
						boincerror(retval));
				exit(retval);
			}
			markTaskAsRunning(job.idreceptor, job.idligand);
		}
	}
	mysql_free_result(res_set);

	return 0;
}

int Connector::markTaskAsRunning(std::string receptorId, std::string ligandId) {
	std::string query = "UPDATE tasks SET status=1 WHERE idreceptor="
			+ receptorId + " and idligand=" + ligandId;

	std::string end = ";";

	mysql_query(connect, (query + end).c_str());
	return 0;
}

int Connector::resetAllTaskRunningIds() {
	std::string query = "UPDATE tasks SET status=0;";

	mysql_query(connect, query.c_str());
	return 0;
}

int Connector::read_sql_config() {

	int i = 0;
	string line;
	string listCreds[4];
	ifstream sql_config(sql_config_file);
	if (sql_config.is_open()) {
		while (getline(sql_config, line)) {
			if(line.at(0) == '#') continue;
			listCreds[i++] = line;
		}
		sql_config.close();
	} else {
		cout << "Fail " << endl;
		return 1;
	}
	creds.host = listCreds[0];
	creds.usr = listCreds[1];
	creds.pwd = listCreds[2];
	creds.base = listCreds[3];
	cout << listCreds[0] << endl;
	return 0;
}
void generator(Connector connect, int cushion) {
	int retval;
	while (1) {
		check_stop_daemons();
		int n;
		retval = count_unsent_results(n, 0);
		if (n > cushion || fileExists("stop_working")) {
			log_messages.printf(MSG_DEBUG, "N > cushion sleep n= %d\n", n);
			log_messages.printf(MSG_DEBUG, "sleep cushion= %d\n", cushion);
			sleep(100);
		} else {
			log_messages.printf(MSG_DEBUG, "N < cushion run n= %d\n", n);
			log_messages.printf(MSG_DEBUG, "run cushion= %d\n", cushion);
			connect.connectDB();
			connect.getAllTasks();
			connect.disconnectDB();
			sleep(100);
		}
	}
}

void usage(char *name) {
	fprintf(stderr,
			"Usage: %s [OPTION]...\n\n"
					"Options:\n"
					"  [ --app X                Application name (default: vina)\n"
					"  [ --in_template_file     Input template (default: vina_wu.xml)\n"
					"  [ --out_template_file    Output template (default: vina_out.xml)\n"
					"  [ -d X ]                 Sets debug level to X.\n"
					"  [ -h | --help ]          Shows this help text.\n"
					"  [ -v | --version ]       Shows version information.\n",
			name);
}

int main(int argc, char** argv) {
	int i, retval;
	char buff[256];

	int cushion = 1000;

	for (i = 1; i < argc; i++) {
		if (is_arg(argv[i], "d")) {
			if (!argv[++i]) {
				log_messages.printf(MSG_CRITICAL, "%s requires an argument\n\n",
						argv[--i]);
				usage(argv[0]);
				exit(1);
			}
			int dl = atoi(argv[i]);
			log_messages.set_debug_level(dl);
			if (dl == 4)
				g_print_queries = true;
		} else if (!strcmp(argv[i], "--app")) {
			app_name = argv[++i];
		} else if (!strcmp(argv[i], "--in_template_file")) {
			in_template_file = argv[++i];
		} else if (!strcmp(argv[i], "--out_template_file")) {
			out_template = argv[++i];
		} else if (!strcmp(argv[i], "--conf")) {
			sql_config_file = argv[++i];
		} else if (is_arg(argv[i], "h") || is_arg(argv[i], "help")) {
			usage(argv[0]);
			exit(0);
		} else if (!strcmp(argv[i], "--cushion")) {
			cushion = atoi(argv[++i]);
		} else if (is_arg(argv[i], "v") || is_arg(argv[i], "version")) {
			printf("%s\n", SVN_VERSION);
			exit(0);
		} else {
			log_messages.printf(MSG_CRITICAL,
					"unknown command line argument: %s\n\n", argv[i]);
			usage(argv[0]);
			exit(1);
		}
	}

	retval = config.parse_file();
	if (retval) {
		log_messages.printf(MSG_CRITICAL, "Can't parse config.xml: %s\n",
				boincerror(retval));
		exit(1);
	}

	retval = boinc_db.open(config.db_name, config.db_host, config.db_user,
			config.db_passwd);
	if (retval) {
		log_messages.printf(MSG_CRITICAL, "can't open db\n");
		exit(1);
	}

	sprintf(buff, "where name='%s'", app_name);
	if (app.lookup(buff)) {
		log_messages.printf(MSG_CRITICAL, "can't find app %s\n", app_name);
		exit(1);
	}

	sprintf(buff, "%s%s", template_path, in_template_file);
	if (read_file_malloc(config.project_path(buff), in_template)) {
		log_messages.printf(MSG_CRITICAL, "can't read input template %s\n",
				buff);
		exit(1);
	}

	start_time = time(0);
	seqno = 0;

	log_messages.printf(MSG_NORMAL, "Starting\n");

	Connector connect;
	if (connect.read_sql_config()) {
		log_messages.printf(MSG_CRITICAL, "can't find base configuration\n");
		exit(1);
	}

	generator(connect, cushion);
}
