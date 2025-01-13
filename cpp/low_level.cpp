#include "Eigen/Dense"
#include <chrono>
#include <cpr/cpr.h>
#include <iostream>
#include <nlohmann/json.hpp>
#include <omp.h>
#include <string>

using json = nlohmann::json;
using namespace std;
using namespace std::chrono;

class Task {
private:
  Eigen::MatrixXf A;
  Eigen::VectorXf b;
  Eigen::VectorXf x;
  string identifier;
  float time;
  int size;

public:
  Task(std::string answer) {
    json task_data;
    try {
      task_data = json::parse(answer);
    } catch (json::parse_error &e) {
      cerr << "JSON parsing error: " << e.what() << endl;
      exit(EXIT_FAILURE);
    }

    auto matrixA = task_data["a"];
    auto matrixb = task_data["b"];

    int rowsA = matrixA.size();
    int colsA = matrixA[0].size();
    A.resize(rowsA, colsA);

    for (int i = 0; i < rowsA; i++)
      for (int j = 0; j < colsA; j++)
        A(i, j) = matrixA[i][j];

    int rowsb = matrixb.size();
    b.resize(rowsb);

    for (int i = 0; i < rowsb; i++)
      b(i) = matrixb[i];

    x.resize(rowsb);

    identifier = task_data["identifier"];
    time = 0.0f;
    size = task_data["size"];
  }

  void work() {
    omp_set_num_threads(8);
    Eigen::setNbThreads(8);
    auto start = high_resolution_clock::now();
    x = A.householderQr().solve(b);

    auto end = high_resolution_clock::now();
    time = duration<float>(end - start).count();
  }

  Eigen::VectorXf get_x() const { return x; }
  Eigen::MatrixXf get_A() const { return A; }
  Eigen::VectorXf get_b() const { return b; }
  string get_identifier() const { return identifier; }
  float get_time() const { return time; }
  int get_size() const { return size; }

  json to_json() const {
    json j;
    j["identifier"] = identifier;

    j["a"] = json::array();
    for (int i = 0; i < A.rows(); ++i) {
      json row = json::array();
      for (int j = 0; j < A.cols(); ++j) {
        row.push_back(A(i, j));
      }
      j["a"].push_back(row);
    }

    j["b"] = json::array();
    for (int i = 0; i < b.size(); ++i) {
      j["b"].push_back(b(i));
    }

    j["x"] = json::array();
    for (int i = 0; i < x.size(); ++i) {
      j["x"].push_back(x(i));
    }

    j["time"] = time;
    j["size"] = size;

    return j;
  }
};

Task get_task(string URL, string ACCESS_KEY) {
  cpr::Response r = cpr::Get(cpr::Url{URL}, cpr::Bearer{ACCESS_KEY});

  if (r.status_code != 200) {
    cerr << "HTTP request failed with status: " << r.status_code << endl;
    exit(EXIT_FAILURE);
  }

  Task task(r.text);
  return task;
}

void do_task_then_post_result(Task task, string URL) {
  cout << "Task (" << task.get_identifier() << ") Started!" << endl;

  task.work();
  json post_data = task.to_json();

  cpr::Response r =
      cpr::Post(cpr::Url{URL}, cpr::Body{post_data.dump()},
                cpr::Header{{"Content-Type", "application/json"}});

  if (r.status_code != 200) {
    cerr << "HTTP POST failed with status: " << r.status_code << endl;
  } else {
    Eigen::VectorXf out(task.get_A().rows());
#pragma omp parallel for
    for (int i = 0; i < task.get_A().rows(); ++i) {
      out(i) = task.get_A().row(i).dot(task.get_x());
    }

    if ((out - task.get_b()).norm() <= 1e-4)
      cout << "Calculation correct!" << endl;

    cout << "Task results (" << task.get_identifier()
         << ") successfully posted!" << endl;
    cout << "Task duration: " << task.get_time() << " seconds" << endl;
  }
}

int main(int argc, char **argv) {
  string URL = "http://127.0.0.1:8000/";
  string POST_URL = "http://127.0.0.1:8000/";
  string ACCESS_KEY = "abracadabra";

  while (true) {
    try {
      Task task = get_task(URL, ACCESS_KEY);
      do_task_then_post_result(task, POST_URL);
    } catch (const std::exception &e) {
      cerr << "An error occurred: " << e.what() << endl;
      return EXIT_FAILURE;
    }
  }
  return EXIT_SUCCESS;
}
