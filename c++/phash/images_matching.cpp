#include <stdio.h>
#include <dirent.h>
#include <errno.h>
#include <vector>
#include <algorithm>
#include <limits>
#include <numeric>
#include <iostream>
#include <string>
#include <experimental/filesystem>
#include <thread>
#include <future>
#include <cassert>

#include "pHash.h"

using namespace std;
using namespace std::experimental;


//data structure for a hash and id
struct ph_imagepoint{
    ulong64 hash;
    filesystem::path id;
};


ulong64 worker(const char* path) {
    ulong64 res;
    ph_dct_imagehash(path, res);
    return res;
}

int main(int argc, char **argv) {

    if (argc < 3){
        printf("no input args\n");
        printf("expected: \"test_imagephash [dir name] [dir_name]\"\n");
        exit(1);
    }
    
    const auto files_count = std::distance(filesystem::directory_iterator(argv[1]), filesystem::directory_iterator());
    vector<string> ids1;
    for (const auto& f: filesystem::directory_iterator(argv[1]))
        ids1.push_back(f.path().c_str());
    vector<string> ids2;
    for (const auto& f: filesystem::directory_iterator(argv[2]))
        ids2.push_back(f.path().c_str());
    
    vector<future<ulong64>> futures1;
    vector<future<ulong64>> futures2;
    for (int i = 0; i < files_count; ++i) {
        futures1.push_back(async(worker, ids1[i].c_str()));
        futures2.push_back(async(worker, ids2[i].c_str()));
    }

    vector<ph_imagepoint> hashlist1; //for hashes in first directory
    for (int i = 0; i < files_count; ++i) {
        hashlist1.push_back(ph_imagepoint{futures1[i].get(), ids1[i]});
    }

    vector<ph_imagepoint> hashlist2; //for hashes in second directory
    for (int i = 0; i < files_count; ++i) {
        hashlist2.push_back(ph_imagepoint{futures2[i].get(), ids2[i]});
    }

    sort(begin(hashlist1), end(hashlist1), [](const ph_imagepoint& lhs, const ph_imagepoint& rhs) { return (lhs.id < rhs.id); });

    for (const auto& e1: hashlist1) {
        int best_distance = numeric_limits<int>::max();
        filesystem::path best_id;
        for (const auto& e2: hashlist2) {
            auto distance = ph_hamming_distance(e1.hash, e2.hash);
            //std::cout << "distance(" << e1.id << ", " << e2.id << ") = " << distance << '\n';
            if (distance < best_distance) {
                best_distance = distance;
                best_id = e2.id;
            }
        }
        //std::cout << hashlist1[i].id << " ========= " << best_id << "  |   " << best_distance << '\n';
	std::cout << e1.id.filename() << "," << best_id.filename() << '\n';
	//std::cout << best_distance << '\n';
    }

    return 0;
}