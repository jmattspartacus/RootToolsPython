void PyEnableImplicitMT(UInt_t num_worker = 8)
{
    ROOT::EnableThreadSafety();
    ROOT::EnableImplicitMT(num_worker);
}