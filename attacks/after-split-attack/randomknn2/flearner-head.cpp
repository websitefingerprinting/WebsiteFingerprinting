#include <iostream>
#include <fstream>
#include <cmath>
#include <string>
#include <string.h>
#include <sstream>
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <algorithm>
#include <map>
//#include "loader.h"
using namespace std;

//Data parameters
int FEAT_NUM = 1225; //number of features
int ROUND_NUM = 16000;
int NEIGHBOUR_NUM = 3; //number of neighbors for kNN
int RECOPOINTS_NUM = 5; //number of neighbors for distance learning
int TRAIN_CLOSED_SITENUM, TRAIN_CLOSED_INSTNUM, TRAIN_OPEN_INSTNUM, 
    TEST_CLOSED_SITENUM, TEST_CLOSED_INSTNUM, TEST_OPEN_INSTNUM;
int OPEN_MAJORITY = 1;
map<string, string> d;

bool inarray(int ele, int* array, int len) {
	for (int i = 0; i < len; i++) {
		if (array[i] == ele)
			return 1;
	}
	return 0;
}

void alg_init_weight(float* weight) {
	for (int i = 0; i < FEAT_NUM; i++) {
		weight[i] = (rand() % 100) / 100.0 + 0.5;
	}
}

float dist(float* feat1, float* feat2, float* weight) {
	float toret = 0;
	for (int i = 0; i < FEAT_NUM; i++) {
		if (feat1[i] != -1 and feat2[i] != -1) {
			toret += weight[i] * abs(feat1[i] - feat2[i]);
		}
	}
	return toret;
}

void alg_recommend2(float** feat, int* featclasses, int featlen, float* weight) {
	float* distlist = new float[featlen];
	int* recogoodlist = new int[RECOPOINTS_NUM];
	int* recobadlist = new int[RECOPOINTS_NUM];
	for (int i = 0; i < featlen; i++) {
		int id = i % featlen;
		i += 8;
		// printf("point: %d out of %d\n", id, featlen);
		if(id%100 == 0){
			printf("\rLearning weights... %d (%d-%d)", id, 0, featlen);
			fflush(stdout);
		}

		int trueclass = featclasses[id];

/*
		int cur_site, cur_inst;
		if (id < CLOSED_SITENUM * CLOSED_INSTNUM) {
			cur_site = id/CLOSED_INSTNUM;
			cur_inst = id % CLOSED_INSTNUM;
		}
		else {
			cur_site = CLOSED_SITENUM;
			cur_inst = id - CLOSED_SITENUM * CLOSED_INSTNUM;
		}
*/

		//learn distance to other feat elements, put in distlist
		for (int k = 0; k < featlen; k++) {
			distlist[k] = dist(feat[id], feat[k], weight);
		}
		//set my own distance to max
		float max = *max_element(distlist, distlist+featlen);
		distlist[id] = max;

		float pointbadness = 0;
		float maxgooddist = 0; //the greatest distance of all the good neighbours NEIGHBOUR_NUM
		
		//find the good neighbors: NEIGHBOUR_NUM lowest distlist values of the same class
		for (int k = 0; k < RECOPOINTS_NUM; k++) {
			int minind; //ind of minimum element of distlist
			float mindist = max;
			for (int dind = 0; dind < featlen; dind++) {
				if (featclasses[dind] == trueclass and distlist[dind] < mindist) {
					minind = dind;
					mindist = distlist[dind];
				}
			}
			if (distlist[minind] > maxgooddist) maxgooddist = distlist[minind];
			distlist[minind] = max;
			recogoodlist[k] = minind;
		}
		for (int dind = 0; dind < featlen; dind++) {
			if (featclasses[dind] == trueclass) {
				distlist[dind] = max;
			}
		}
		for (int k = 0; k < RECOPOINTS_NUM; k++) {
			int ind = min_element(distlist, distlist+featlen) - distlist;
			if (distlist[ind] <= maxgooddist) pointbadness += 1;
			distlist[ind] = max;
			recobadlist[k] = ind;
		}

		pointbadness /= float(RECOPOINTS_NUM);
		pointbadness += 0.2;
		/*
		if (i == 0) {
			float gooddist = 0;
			float baddist = 0;
			printf("Current point: %d\n", i);
			printf("Bad points:\n");
			for (int k = 0; k < RECOPOINTS_NUM; k++) {
				printf("%d, %f\n", recobadlist[k], dist(feat[i], feat[recobadlist[k]], weight));	
				baddist += dist(feat[i], feat[recobadlist[k]], weight);
			}

			printf("Good points:\n");
			for (int k = 0; k < RECOPOINTS_NUM; k++) {
				printf("%d, %f\n", recogoodlist[k], dist(feat[i], feat[recogoodlist[k]], weight));
				gooddist += dist(feat[i], feat[recogoodlist[k]], weight);
			}

			printf("Total bad distance: %f\n", baddist);
			printf("Total good distance: %f\n", gooddist);
		}*/

		float* featdist = new float[FEAT_NUM];
		for (int f = 0; f < FEAT_NUM; f++) {
			featdist[f] = 0;
		}
		int* badlist = new int[FEAT_NUM];
		int minbadlist = 0;
		int countbadlist = 0;
		//printf("%d ", badlist[3]);
		for (int f = 0; f < FEAT_NUM; f++) {
			if (weight[f] == 0) badlist[f] = 0;
			else {
			float maxgood = 0;
			int countbad = 0;
			for (int k = 0; k < RECOPOINTS_NUM; k++) {
				float n = abs(feat[id][f] - feat[recogoodlist[k]][f]);
				if (feat[id][f] == -1 or feat[recogoodlist[k]][f] == -1) 
					n = 0;
				if (n >= maxgood) maxgood = n;
			}
			for (int k = 0; k < RECOPOINTS_NUM; k++) {
				float n = abs(feat[id][f] - feat[recobadlist[k]][f]);
				if (feat[id][f] == -1 or feat[recobadlist[k]][f] == -1) 
					n = 0;
				//if (f == 3) {
				//	printf("%d %d %f %f\n", i, k, n, maxgood);
				//}
				featdist[f] += n;
				if (n <= maxgood) countbad += 1;
			}
			badlist[f] = countbad;
			if (countbad < minbadlist) minbadlist = countbad;	
			}
		}

		for (int f = 0; f < FEAT_NUM; f++) {
			if (badlist[f] != minbadlist) countbadlist += 1;
		}
		int* w0id = new int[countbadlist];
		float* change = new float[countbadlist];

		int temp = 0;
		float C1 = 0;
		float C2 = 0;
		for (int f = 0; f < FEAT_NUM; f++) {
			if (badlist[f] != minbadlist) {
				w0id[temp] = f;
				change[temp] = weight[f] * 0.02 * badlist[f]/float(RECOPOINTS_NUM); //* pointbadness;
				//if (change[temp] < 1.0/1000) change[temp] = weight[f];
				C1 += change[temp] * featdist[f];
				C2 += change[temp];
				weight[f] -= change[temp];
				temp += 1;
			}
		}

		/*if (i == 0) {
			printf("%d %f %f\n", countbadlist, C1, C2);
			for (int f = 0; f < 30; f++) {
				printf("%f %f\n", weight[f], featdist[f]);
			}
		}*/
		float totalfd = 0;
		for (int f = 0; f < FEAT_NUM; f++) {
			if (badlist[f] == minbadlist and weight[f] > 0) {
				totalfd += featdist[f];
			}
		}

		for (int f = 0; f < FEAT_NUM; f++) {
			if (badlist[f] == minbadlist and weight[f] > 0) {
				weight[f] += C1/(totalfd);
			}
		}

		/*if (i == 0) {
			printf("%d %f %f\n", countbadlist, C1, C2);
			for (int f = 0; f < 30; f++) {
				printf("%f %f\n", weight[f], featdist[f]);
			}
		}*/

		/*if (i == 0) {
			float gooddist = 0;
			float baddist = 0;
			printf("Current point: %d\n", i);
			printf("Bad points:\n");
			for (int k = 0; k < RECOPOINTS_NUM; k++) {
				printf("%d, %f\n", recobadlist[k], dist(feat[i], feat[recobadlist[k]], weight));	
				baddist += dist(feat[i], feat[recobadlist[k]], weight);
			}

			printf("Good points:\n");
			for (int k = 0; k < RECOPOINTS_NUM; k++) {
				printf("%d, %f\n", recogoodlist[k], dist(feat[i], feat[recogoodlist[k]], weight));
				gooddist += dist(feat[i], feat[recogoodlist[k]], weight,);
			}

			printf("Total bad distance: %f\n", baddist);
			printf("Total good distance: %f\n", gooddist);
		}*/
		
		delete[] featdist;
		delete[] w0id;
		delete[] change;
		delete[] badlist;
	}


	/*for (int j = 0; j < FEAT_NUM; j++) {
		if (weight[j] > 0)
			weight[j] *= (0.9 + (rand() % 100) / 500.0);
	}*/
	printf("\n");
	delete[] distlist;
	delete[] recobadlist;
	delete[] recogoodlist;



}

void accuracy(float** trainfeat, float** testfeat, int* trainfeatclasses, int* testfeatclasses, int trainlen, int testlen, float* weight) {
	float* distlist = new float[trainlen];

	printf("trainlen %d testlen %d\n", trainlen, testlen);

	int tp = 0;
	int fp = 0;
	int wp = 0;
	int p = 0;
	int n = 0;
	for (int is = 0; is < testlen; is++) {

		int trueclass = testfeatclasses[is];
		

		map<int, int> classlist;
		//printf("\rComputing accuracy... %d (%d-%d)\n", is, 0, testlen-1);
		//fflush(stdout);
		for (int at = 0; at < trainlen; at++) {
			distlist[at] = dist(testfeat[is], trainfeat[at], weight);
		}
		float max = *max_element(distlist, distlist+trainlen);

		//log the match score of each class
		FILE * flog;
		flog = fopen("flearner.results", "a");
		fprintf(flog, "%d", trueclass);

		int CLASS_NUM = atoi(d["CLOSED_SITENUM"].c_str());
		if (atoi(d["OPEN_INSTNUM"].c_str()) > 0) CLASS_NUM += 1;

		map<int, float> match;
		for (int i = 0; i < CLASS_NUM; i++) {
			match[i] = max;
		}
		for (int at = 0; at < trainlen; at++) {
			int classind = trainfeatclasses[at];
			if (classind == -1) classind = CLASS_NUM-1;
			if (distlist[at] < match[classind]) match[classind] = distlist[at];
		}
		//additive inverse is match

		for (int i = 0; i < CLASS_NUM; i++) {
			match[i] = max - match[i];
			fprintf(flog, "\t%f", match[i]);
		}
		fprintf(flog, "\n");
		
		int guessclass = 0;
		int maxclass = 0;

		for (int i = 0; i < NEIGHBOUR_NUM; i++) {
			int ind = find(distlist, distlist + trainlen, *min_element(distlist, distlist+trainlen)) - distlist;
			int classind = trainfeatclasses[ind];
			if(classlist.find(classind) == classlist.end()) classlist[classind] = 1;
			else classlist[classind] += 1;

			if (classlist[classind] > maxclass) {
				maxclass = classlist[classind];
				guessclass = classind;
			}
			distlist[ind] = max;
		}

		
		
		if (OPEN_MAJORITY == 1) {
			float hasconsensus = 0;
			/*float score1 = 1.4; 
			float score2 = 0; //score1 >= score2
			float score3 = 1;
			hasconsensus += classlist[guessclass] * score1;
			for (int i = 0; i < CLOSED_SITENUM; i++) {
				hasconsensus -= classlist[i] * score2;
			}
			if (OPEN_INSTNUM > 0) hasconsensus -= classlist[CLOSED_SITENUM] * score3;*/
			if (classlist[guessclass] == NEIGHBOUR_NUM) hasconsensus = 1;
			/*if (hasconsensus > 0 and guessclass != CLOSED_SITENUM) {		
				//double check consensus: if distance is too high, it also doesn't work
				//repeat 100 times
				
				float d_true = 0;
				int ind1, ind2;
			
				for (int i = 0; i < 20; i++) {
					ind1 = guessclass * CLOSED_INSTNUM + rand() % CLOSED_INSTNUM;
					float min = -1;
					float cur_d = 0;
				
					for (int j = 0; j < CLOSED_INSTNUM; j++) {
						ind2 = guessclass * CLOSED_INSTNUM + j;
						if (ind2 != ind1) {
							cur_d = dist(trainfeat[ind1], trainfeat[ind2], weight);
							if (cur_d < min or min == -1) min = cur_d;
						}
					}
					
					d_true += min;
				}
				d_true /= 20;
				
				//printf("d_true: %f, d_guess: %f", d_true, d_guess);
				
				if (d_guess > d_true * 1.25) {
					hasconsensus = -1;
				}
				
				
			}*/
		
		
			if (hasconsensus <= 0) {
				guessclass = -1;
			}
		}
		if (guessclass != -1) {
			if (trueclass == guessclass) tp += 1;
			else if(trueclass != -1){
				wp += 1;
			} 
			else{
				fp += 1;
			}

		}
		if (trueclass == -1) n += 1;
		else p += 1;

		// cout<<"True: "<<trueclass<<" ,guess: "<<guessclass<<endl;
		// printf("%d %d %d %d %d\n", tp, wp, fp, p, n);
		printf("testid: %d\tguess: %d\n",trueclass, guessclass);
		fclose(flog);
	}

	printf("\n");

	delete[] distlist;
}

//reads fname (a file name) for a single file
void read_feat(float* feat, string fname) {
	ifstream fread;
	fread.open(fname.c_str());
	int cnt = 0;
	while(fread.peek() != EOF){
		string str = "";
		getline(fread,str);
		if(str.c_str()[1] == 'X')
			feat[cnt++] = -1;
		else{
			feat[cnt++] = atof(str.c_str());
		}
		//cout<<cnt-1<<" " << feat[cnt-1]<<endl;
	}
	fread.close();
	// string str = "";
	// getline(fread, str);
	// fread.close();

	// string tempstr = "";
	// int feat_count = 0;
	// for (int i = 0; i < str.length(); i++) {
	// 	if (str[i] == ' ') {
	// 		if (tempstr.c_str()[1] == 'X') {
	// 			feat[feat_count] = -1;
	// 		}
	// 		else {
	// 			feat[feat_count] = atof(tempstr.c_str());
	// 		}	
	// 		feat_count += 1;
	// 		tempstr = "";
	// 	}
	// 	else {
	// 		tempstr += str[i];
	// 	}
	// }

}

void read_filelist(float ** feat, int * featclasses, int featlen, string fname) {
	ifstream fread;
	fread.open(fname.c_str());
	
	int readcount = 0;
	while (fread.peek() != EOF) {
		string str = "";
		string rstr = "";
		getline(fread, rstr);
		int found = rstr.find_last_of("/");
		str = rstr.substr(found+1);
		str = str.substr(0, str.find_first_of("."));
		//closed or open?
		if (str.find("-") != string::npos) {
			//this means closed
			string str1 = str.substr(0, str.find_first_of("-"));
			string str2 = str.substr(str.find_first_of("-")+1);
			int s = atoi(str1.c_str());
			int i = atoi(str2.c_str());
			read_feat(feat[readcount], rstr);
			featclasses[readcount] = s;
		}
		else {
			//this means open
			read_feat(feat[readcount], rstr);
			featclasses[readcount] = -1;
		}
		readcount += 1;
	}
}

int read_filelen(string fname) {
	int featlen = 0;
	
	//one round to learn the length... 
	ifstream fread;
	fread.open(fname.c_str());
	while (fread.peek() != EOF) {
		string str = "";
		getline(fread, str);
		featlen += 1;
	}
	fread.close();
	
	return featlen;
}

void read_options(string fname) {
//	std::map <string, string> d;
	ifstream fread;
	fread.open(fname.c_str());
	while (fread.peek() != EOF) {
		string str = "";
		getline(fread, str);

		while (str.find("#") != string::npos)
			str = str.substr(0, str.find_first_of("#"));
		if (str.find("\t") != string::npos) {
			string optname = str.substr(0, str.find_first_of("\t"));
			string optval = str.substr(str.find_first_of("\t")+1);
			d[optname] = optval;
		}
	}
	fread.close();
}

// int get_featnum(string folder) {
// 	//Guess feat num so feat set can be changed without changing this code	
// 	ostringstream freadnamestream;
// 	freadnamestream << folder << "0-2.cellkNN";
// 	string freadname = freadnamestream.str();
	
// 	ifstream fread;
// 	fread.open(freadname.c_str());
// 	// string str = "";
// 	// getline(fread, str);
// 	int feat_count = 0;
// 	while(fread.peek()!=EOF){
// 		string str = "";
// 		getline(fread, str);
// 		feat_count += 1;
// 	}

// 	fread.close();

// 	// int feat_count = 0;
// 	// for (int i = 0; i < str.length(); i++) {
// 	// 	if (str[i] == ' ') {
// 	// 		feat_count += 1;
// 	// 	}
// 	// }
// 	return feat_count;
// }


string findFileName(string s){
	int n = s.find_last_of('/');
	s = s.substr(0,n);
	n = s.find_last_of('/');
	return s.substr(n+1, s.size()).c_str();
}

int main(int argc, char** argv) {
	/*int OPENTEST_list [6] = {100, 500, 1000, 3000, 5000, 6000};
	int NEIGHBOUR_list [10] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

	if(argc == 3){
		int OPENTEST_ind = atoi(argv[1]); 
		int NEIGHBOUR_ind = atoi(argv[2]);

		OPEN_INSTNUM = OPENTEST_list[OPENTEST_ind % 5];
		NEIGHBOUR_NUM = NEIGHBOUR_list[NEIGHBOUR_ind % 10];
	}*/

	srand(time(NULL));

	if(argc != 4){
	    cout <<"call: ./flearner optname"<<endl;
	    exit(1);
	}

	char* optionname = argv[1];
	char* data_name = argv[2]; //train
	char* test_data = argv[3]; //test

	read_options(string(optionname));

	string train_name = findFileName(data_name);
	string test_name = findFileName(test_data);

	string data_path = string(d["OUTPUT_LOC"]);
	string trainlist  = data_path + string(train_name)+'/' + "trainlist";
	string testlist = data_path + string(test_name) +'/' + "testlist-head";



	// cout<<data_path<<endl;
	// cout<<trainlist<<endl;
	// cout<<testlist<<endl;


	// FEAT_NUM = get_featnum(data_path+"/"+data_name+"/");
	// cout<<"feature num is "<<FEAT_NUM<<endl;
	// cout<<data_path+"/"+data_name+"/"<<endl;
	//learn weights
	int wlen = read_filelen(trainlist);

	float** wfeat = new float*[wlen];
	int * wfeatclasses;
	for (int i = 0; i < wlen; i++) {
		wfeat[i] = new float[FEAT_NUM];
	}
	wfeatclasses = new int[wlen];


	printf("here %d %d\n", FEAT_NUM, wlen);
	// for(int i = 0; i< 1; i++)
	// 	for(int j=0;j<10;j ++)
	// 		cout<<wfeat[i][j]<<" ";
	// cout<<endl;


	read_filelist(wfeat, wfeatclasses, wlen, trainlist);

	// for(int i = 0; i <10;i++)
	// 	cout<<i<<": class:"<<wfeatclasses[i]<<endl;
	
	float * weight = new float[FEAT_NUM];
	alg_init_weight(weight);
	cout<<"Init weights.."<<endl;
	// for(int i=0;i<10;i++)
	// 	cout<<weight[i]<<" ";
	// cout<<endl;


	clock_t t1, t2;
	float train_time, test_time;
	t1 = clock();
	alg_recommend2(wfeat, wfeatclasses, wlen, weight);
	t2 = clock();
	train_time = (t2 - t1)/float(CLOCKS_PER_SEC);
	// for(int i=0;i<10;i++)
	// 	cout<<weight[i]<<" ";
	// cout<<endl;
	
	// // //load training instances
	// // float** trainfeat;
	// // int * trainfeatclasses;
	// // int trainlen = read_filelen(d["TRAIN_LIST"]);
	// // trainfeat = new float*[trainlen];
	// // for (int i = 0; i < trainlen; i++) {
	// // 	trainfeat[i] = new float[FEAT_NUM];
	// // }
	// // trainfeatclasses = new int[trainlen];
	// // read_filelist(trainfeat, trainfeatclasses, trainlen, d["TRAIN_LIST"]);

	//Load testing instances
	float** testfeat;
	int * testfeatclasses;
	int testlen = read_filelen(testlist);
	testfeat = new float*[testlen];
	for (int i = 0; i < testlen; i++) {
		testfeat[i] = new float[FEAT_NUM];
	}
	testfeatclasses = new int[testlen];
	read_filelist(testfeat, testfeatclasses, testlen, testlist);


	printf("Training and testing instances loaded\n");
	
	// for(int i=0;i<10;i++)
	// 	cout<<weight[i]<<" ";
	// cout<<endl;
	// for(int i = 0;i<1;i++){
	// 	for(int j=0;j<10;j++)
	// 		cout<<wfeat[i][j]<<" ";
	// 	cout<<endl;

	// }
	// cout<<"---"<<endl;
	// for(int i = 0;i<1;i++){
	// 	for(int j=0;j<10;j++)
	// 		cout<<testfeat[i][j]<<" ";
	// 	cout<<endl;
		
	// }

	int tpc, tnc, pc, nc;
	t1 = clock();
	accuracy(wfeat, testfeat, wfeatclasses, testfeatclasses, wlen, testlen, weight);
	t2 = clock();
	test_time = (t2 - t1)/float(CLOCKS_PER_SEC);

	for (int i = 0; i < wlen; i++) {
		delete[] wfeat[i];
	}
	delete[] wfeat;
	// for (int i = 0; i < trainlen; i++) {
	// 	delete[] trainfeat[i];
	// }
	// delete[] trainfeat;
	for (int i = 0; i < testlen; i++) {
		delete[] testfeat[i];
	}
	delete[] testfeat;

	delete[] weight;
	return 0;
}
