//********************************************************//
// CUDA SIFT extractor by Marten Björkman aka Celebrandil //
//              celle @ csc.kth.se                       //
//********************************************************//  

#include <iostream>
#include <cmath>
#include <iomanip>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

#include <filesystem>
#include <vector>
#include <algorithm>
#include <fstream>
#include <chrono>


#include "cudaImage.h"
#include "cudaSift.h"

int ImproveHomography(SiftData &data, float *homography, int numLoops, float minScore, float maxAmbiguity, float thresh);
void PrintMatchData(SiftData &siftData1, SiftData &siftData2, CudaImage &img);
void MatchAll(SiftData &siftData1, SiftData &siftData2, float *homography);

double ScaleUp(CudaImage &res, CudaImage &src);

bool equal(const cv::Mat & a, const cv::Mat & b)
{
	if ((a.rows != b.rows) || (a.cols != b.cols))
		return false;
	cv::Scalar s = cv::sum(a - b);
	return (s[0] == 0) && (s[1] == 0) && (s[2] == 0);
}






void MatchAll(SiftData &siftData1, SiftData &siftData2, float *homography)
{
#ifdef MANAGEDMEM
  SiftPoint *sift1 = siftData1.m_data;
  SiftPoint *sift2 = siftData2.m_data;
#else
  SiftPoint *sift1 = siftData1.h_data;
  SiftPoint *sift2 = siftData2.h_data;
#endif
  int numPts1 = siftData1.numPts;
  int numPts2 = siftData2.numPts;
  int numFound = 0;
#if 1
  homography[0] = homography[4] = -1.0f;
  homography[1] = homography[3] = homography[6] = homography[7] = 0.0f;
  homography[2] = 1279.0f;
  homography[5] = 959.0f;
#endif
  for (int i=0;i<numPts1;i++) {
    float *data1 = sift1[i].data;
    std::cout << i << ":" << sift1[i].scale << ":" << (int)sift1[i].orientation << " " << sift1[i].xpos << " " << sift1[i].ypos << std::endl;
    bool found = false;
    for (int j=0;j<numPts2;j++) {
      float *data2 = sift2[j].data;
      float sum = 0.0f;
      for (int k=0;k<128;k++) 
	sum += data1[k]*data2[k];    
      float den = homography[6]*sift1[i].xpos + homography[7]*sift1[i].ypos + homography[8];
      float dx = (homography[0]*sift1[i].xpos + homography[1]*sift1[i].ypos + homography[2]) / den - sift2[j].xpos;
      float dy = (homography[3]*sift1[i].xpos + homography[4]*sift1[i].ypos + homography[5]) / den - sift2[j].ypos;
      float err = dx*dx + dy*dy;
      if (err<100.0f) // 100.0
	found = true;
      if (err<100.0f || j==sift1[i].match) { // 100.0
	if (j==sift1[i].match && err<100.0f)
	  std::cout << " *";
	else if (j==sift1[i].match) 
	  std::cout << " -";
	else if (err<100.0f)
	  std::cout << " +";
	else
	  std::cout << "  ";
	std::cout << j << ":" << sum << ":" << (int)sqrt(err) << ":" << sift2[j].scale << ":" << (int)sift2[j].orientation << " " << sift2[j].xpos << " " << sift2[j].ypos << " " << (int)dx << " " << (int)dy << std::endl;
      }
    }
    std::cout << std::endl;
    if (found)
      numFound++;
  }
  std::cout << "Number of finds: " << numFound << " / " << numPts1 << std::endl;
  std::cout << homography[0] << " " << homography[1] << " " << homography[2] << std::endl;//%%%
  std::cout << homography[3] << " " << homography[4] << " " << homography[5] << std::endl;//%%%
  std::cout << homography[6] << " " << homography[7] << " " << homography[8] << std::endl;//%%%
}

void PrintMatchData(SiftData &siftData1, SiftData &siftData2, CudaImage &img)
{
  int numPts = siftData1.numPts;
#ifdef MANAGEDMEM
  SiftPoint *sift1 = siftData1.m_data;
  SiftPoint *sift2 = siftData2.m_data;
#else
  SiftPoint *sift1 = siftData1.h_data;
  SiftPoint *sift2 = siftData2.h_data;
#endif
  float *h_img = img.h_data;
  int w = img.width;
  int h = img.height;
  std::cout << std::setprecision(3);
  for (int j=0;j<numPts;j++) { 
    int k = sift1[j].match;
    if (sift1[j].match_error<5) {
      float dx = sift2[k].xpos - sift1[j].xpos;
      float dy = sift2[k].ypos - sift1[j].ypos;
#if 0
      if (false && sift1[j].xpos>550 && sift1[j].xpos<600) {
	std::cout << "pos1=(" << (int)sift1[j].xpos << "," << (int)sift1[j].ypos << ") ";
	std::cout << j << ": " << "score=" << sift1[j].score << "  ambiguity=" << sift1[j].ambiguity << "  match=" << k << "  ";
	std::cout << "scale=" << sift1[j].scale << "  ";
	std::cout << "error=" << (int)sift1[j].match_error << "  ";
	std::cout << "orient=" << (int)sift1[j].orientation << "," << (int)sift2[k].orientation << "  ";
	std::cout << " delta=(" << (int)dx << "," << (int)dy << ")" << std::endl;
      }
#endif
#if 1
      int len = (int)(fabs(dx)>fabs(dy) ? fabs(dx) : fabs(dy));
      for (int l=0;l<len;l++) {
	int x = (int)(sift1[j].xpos + dx*l/len);
	int y = (int)(sift1[j].ypos + dy*l/len);
	h_img[y*w+x] = 255.0f;
      }
#endif
    }
    int x = (int)(sift1[j].xpos+0.5);
    int y = (int)(sift1[j].ypos+0.5);
    int s = std::min(x, std::min(y, std::min(w-x-2, std::min(h-y-2, (int)(1.41*sift1[j].scale)))));
    int p = y*w + x;
    p += (w+1);
    for (int k=0;k<s;k++) 
      h_img[p-k] = h_img[p+k] = h_img[p-k*w] = h_img[p+k*w] = 0.0f;
    p -= (w+1);
    for (int k=0;k<s;k++) 
      h_img[p-k] = h_img[p+k] = h_img[p-k*w] =h_img[p+k*w] = 255.0f;
  }
  std::cout << std::setprecision(6);
}



int main(int argc, char **argv)
{
	using namespace std;
	using namespace std::filesystem;

	if (argc < 3) {
		cerr << "invalid args\n";
		exit(-1);
	}

	InitCuda(1);

	float initBlur = 1.0f;
	float thresh = 1.f;
	float *memoryTmp = AllocSiftTempMemory(1000, 1000, 5, false);
	const auto nfeatures = 300;

	auto tifs_count = distance(directory_iterator(argv[2]), directory_iterator());

	vector<cv::Mat> tifs_cvimg(tifs_count);
	vector<string> tifs_fnames(tifs_count);
	vector<CudaImage> tifs_img(tifs_count);
	vector<SiftData> tifs_siftdata(tifs_count);
	size_t i = 0;
	unsigned int w, h;
	cout << "Starting Extracting Features from TIFs" << endl;
	for (const auto& f : directory_iterator(argv[2])) {
		//cout << f.path().string() << endl;
		if (i % 1000 == 0) {
			cout << i << endl;
		}
		tifs_fnames[i] = f.path().filename().string();
		//clog << tifs_fnames[i] << endl;

		cv::imread(f.path().string(), 0).convertTo(tifs_cvimg[i], CV_32FC1);
		if (!tifs_cvimg[i].data) {
			clog << "Invalid TIF image\n";
			exit(-1);
		}

		w = tifs_cvimg[i].cols;
		h = tifs_cvimg[i].rows;

		//clog << "w = " << w << " | h = " << h << endl;
		tifs_img[i].Allocate(w, h, iAlignUp(w, 128), false, NULL, (float*)tifs_cvimg[i].data);

		auto duration = tifs_img[i].Download();
		//clog << "Download time: " << duration << endl;

		InitSiftData(tifs_siftdata[i], nfeatures, true, true);
		ExtractSift(tifs_siftdata[i], tifs_img[i], 5, initBlur, thresh, 0.0f, false, memoryTmp);
		//cout << setw(50) << tifs_fnames[i] << setw(50) << tifs_siftdata[i].numPts << endl;
		if (tifs_siftdata[i].numPts > 30)
			++i;
	}
	tifs_count = int(i);

	cout << "Done Extracting Features From TIF" << endl;
	cout << "Count = " << tifs_count << endl;

	ofstream best_out("out_" + to_string(w) + ".csv");
	ofstream nomatch_out("nomatch_" + to_string(w) + ".csv");
	ofstream conflict_out("conflict_" + to_string(w) + ".csv");

	cv::Mat jpeg_cvimg;
	string jpeg_fname;
	CudaImage jpeg_img;
	SiftData jpeg_siftdata;
	cout << "Starting Reading From JPG Directory" << endl;
	auto start_time = chrono::system_clock::now();
	for (const auto& f : directory_iterator(argv[1])) {
		jpeg_fname = f.path().filename().string();
		cv::imread(f.path().string(), 0).convertTo(jpeg_cvimg, CV_32FC1);
		if (!jpeg_cvimg.data) {
			clog << "Invalid JPEG image\n";
			exit(-2);
		}
		unsigned int w = jpeg_cvimg.cols;
		unsigned int h = jpeg_cvimg.rows;

		//clog << "w = " << w << " | h = " << h << endl;
		jpeg_img.Allocate(w, h, iAlignUp(w, 128), false, NULL, (float*)jpeg_cvimg.data);

		auto duration = jpeg_img.Download();
		//clog << "Download time: " << duration << endl;

		InitSiftData(jpeg_siftdata, nfeatures, true, true);
		ExtractSift(jpeg_siftdata, jpeg_img, 5, initBlur, thresh, 0.0f, false, memoryTmp);
		if (jpeg_siftdata.numPts == 0) {
			continue;
		}

		cout << "*** " << jpeg_fname << '\n';
		string best_tif;
		//long long last_best_pts = 0;
		int count_best = 0;
		double best_rate = 0.;
		for (int j = 0; j < tifs_count; ++j) {
			const auto& tif_fname = tifs_fnames[j];
			auto& tif_siftdata = tifs_siftdata[j];
			
			MatchSiftData(jpeg_siftdata, tif_siftdata);

			float homography[9];
			int numMatches;
			FindHomography(jpeg_siftdata, homography, &numMatches, 1000, 0.85f, 0.95f, thresh);
			int numFit = numMatches;
			//int numFit = ImproveHomography(jpeg_siftdata, homography, 5, 0.00f, 0.80f, 3.0);
			if (numFit > std::min(jpeg_siftdata.numPts, tif_siftdata.numPts))
				continue;
			if (tif_siftdata.numPts > 0  && numFit > 0) {
				auto rate = 100.0f*numFit / std::min(jpeg_siftdata.numPts, tif_siftdata.numPts);
				if (rate > 30. && (best_tif == "" || best_rate < rate)) {
					count_best = 1;
					best_rate = rate;
					best_tif = tif_fname;
					//std::cout << std::left << std::setw(50) << jpeg_fname << setw(50) << best_tif << std::setprecision(3) << std::setw(5) << best_rate << '\n';
					//std::cout << std::left << setw(50) << jpeg_siftdata.numPts << setw(50) << tif_siftdata.numPts << setw(50) << numFit << std::setw(50) << rate << '\n';
					//last_best_pts = std::min(jpeg_siftdata.numPts, tif_siftdata.numPts);
				}
				else if (best_tif != "" && std::abs(best_rate - rate) < std::numeric_limits<double>::epsilon()) {
					//std::cout << std::left << std::setw(50) << jpeg_fname << setw(50) << best_tif << std::setprecision(3) << std::setw(5) << best_rate << '\n';
					//std::cout << std::left << setw(50) << jpeg_siftdata.numPts << setw(50) << tif_siftdata.numPts << setw(50) << numFit << std::setw(50) << rate << '\n';
					++count_best;
				}
			}

			std::cout << std::left;
			
			/*
			std::cout << std::setw(30) << tif_fname
				<< "Number of features: " << setw(6) << jpeg_siftdata.numPts
				<< " " << setw(6) << tif_siftdata.numPts
				<< " | Number of matching features: " << setw(6) << numFit
				<< " " << setw(6) << numMatches
				<< " " << setprecision(3) << 100.0f*numFit / std::min(jpeg_siftdata.numPts, tif_siftdata.numPts)
				<< "% " << setprecision(3) << initBlur
				<< " " << setprecision(3) << thresh << '\n';
			*/
		}

		if (count_best == 1) {
			std::cout << std::left << std::setw(50) << jpeg_fname << setw(50) << best_tif << std::setprecision(3) << std::setw(5) << best_rate << '\n';
			best_out << jpeg_fname << "," << best_tif << endl;
		}
		else if (count_best == 0) {
			std::cout << std::left << std::setw(50) << jpeg_fname << std::setw(50) << "NO MATCH\n";
			nomatch_out << jpeg_fname << endl;
		}
		else {
			std::cout << std::left << std::setw(40) << jpeg_fname << "MULTIPLE MATCHES " << " " << count_best << std::setw(40) << best_tif << '\n';
			conflict_out << jpeg_fname << endl;
		}
		std::cout << '\n';

		++i;
	}
	auto end_time = chrono::system_clock::now();
	auto elapsed = chrono::duration_cast<chrono::seconds>(end_time - start_time).count();
	cout << "Duration: " << elapsed << " seconds " << endl;
	best_out.close();
	nomatch_out.close();
	conflict_out.close();

	for (auto& tif_siftdata : tifs_siftdata)
		FreeSiftData(tif_siftdata);

}
