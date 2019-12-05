# Image matching
A collection of algorithms for comparing images similarity I've used to detect duplications in a set of 25000 images that were slightly altered with an adobe tool.

List of methods:
- perceptual hash with (C++ Opencv), fastest and most precise.
- Scale-Invariant feature transform (SIFT) on Cuda (C++), Requires high gpu specs.
- Structural similary, fast but not precise.