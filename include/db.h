#ifndef __ZDC_DB__
#define __ZDC_DB__

#include <iostream>
#include <sstream>
#include <cstring>
#include <string>
#include <sqlite3.h>
#include "utilities.h"
#include "zdc.h"

using namespace std;

const std::string zdcDbName = string(zdc::ZDCROOT) + "/database/NSRL_test.db";
const char* zdcTableName = "runs";

class zdcDB {
  private:
    sqlite3 *db;

  public:
    zdcDB();
    ~zdcDB();
    bool createConnection();
    bool closeConnection();
    vector<int> getRuns(const char* cond);
    string getRunValue(const int run, const char* field);
    string getRunType(const int run);
    string getRunFlag(const int run);
    string getRunStartTime(const int run);
    int getPedRun(const int run);
    int getMIPRun(const int run);
    int getRunEventNumber(const int run);
    int getRunLength(const int run);
    int getRunTrigger(const int run);
    float getRunT1(const int run);
    float getRunT2(const int run);
    float getRunT3(const int run);
    float getRunT4(const int run);
};

zdcDB::zdcDB() 
{
    int rc = sqlite3_open(zdcDbName.c_str(), &db);
    if (rc != SQLITE_OK)
    {
	cerr << FATAL << "Can't connect to the database" << endl;
	exit(4);
    }
}

zdcDB::~zdcDB() 
{
    sqlite3_close(db);
}

vector<int> zdcDB::getRuns(const char* cond)
{
    vector<int> runs;

    sqlite3_stmt* stmt;
    char sql[1024];
    sprintf(sql, "SELECT Run FROM %s WHERE %s", zdcTableName, cond);
    const char* errMsg = 0;
    int rc = sqlite3_prepare_v2(db, sql, strlen(sql), &stmt, &errMsg);
    if (rc == SQLITE_OK)
    {
	while (sqlite3_step(stmt) == SQLITE_ROW) 
	{
	    // Get the data from the current row
	    int run = sqlite3_column_int(stmt, 0); // First column (index 0)
	    runs.push_back(run);
	}
    }
    else
    {
	const char* error = sqlite3_errmsg(db);
	cerr << ERROR << error << endl;;
    }

    sqlite3_finalize(stmt);
    return runs;
}

string zdcDB::getRunValue(const int run, const char* field)
{
    sqlite3_stmt* stmt;
    char sql[1024];
    sprintf(sql, "SELECT %s FROM %s WHERE Run = %d", field, zdcTableName, run);
    const char* errMsg = 0;
    int rc = sqlite3_prepare_v2(db, sql, strlen(sql), &stmt, &errMsg);
    if (rc != SQLITE_OK)
    {
	const char* error = sqlite3_errmsg(db);
	cerr << ERROR << error << endl;;
	sqlite3_finalize(stmt);
	return "";
    }

    rc = sqlite3_step(stmt);
    if (rc != SQLITE_ROW)
    {
	sqlite3_finalize(stmt);
	return "";
    }

    const unsigned char* value = sqlite3_column_text(stmt, 0);
    stringstream ss;
    ss << value;

    sqlite3_finalize(stmt);

    return ss.str();
}

string zdcDB::getRunType(const int run)
{
    return getRunValue(run, "Type");
}

string zdcDB::getRunFlag(const int run)
{
    return getRunValue(run, "Flag");
}

string zdcDB::getRunStartTime(const int run)
{
    return getRunValue(run, "StartTime");
}

int zdcDB::getPedRun(const int run)
{
    return stoi(getRunValue(run, "PedRun"));
}

int zdcDB::getMIPRun(const int run)
{
    return stoi(getRunValue(run, "MIPRun"));
}

int zdcDB::getRunEventNumber(const int run)
{
    return stoi(getRunValue(run, "Events"));
}

int zdcDB::getRunLength(const int run)
{
    return stoi(getRunValue(run, "Length"));
}

int zdcDB::getRunTrigger(const int run)
{
    return stoi(getRunValue(run, "Trigger"));
}

float zdcDB::getRunT1(const int run)
{
    return stof(getRunValue(run, "T1"));
}

float zdcDB::getRunT2(const int run)
{
    return stof(getRunValue(run, "T2"));
}

float zdcDB::getRunT3(const int run)
{
    return stof(getRunValue(run, "T3"));
}

float zdcDB::getRunT4(const int run)
{
    return stof(getRunValue(run, "T4"));
}
#endif
