# fedora_replace_namespace
Python script for replacing Fedora PID namespaces in FOXML files (in place! make a backup copy!).
Takes a file of Fedora PIDs as the input, one PID per line, without info/fedora prefix, e.g.:

```
lat:1839_00_0000_0000_0018_0EC4_4
lat:1839_00_0000_0000_0020_0C28_A
lat:1839_00_0000_0000_0000_9252_A
lat:1839_00_0000_0000_0000_F586_7
lat:1839_00_0000_0000_0021_E1E8_A
lat:1839_00_0000_0000_0017_F9D8_A
```

After running this script, the Fedora rebuild script should be used to rebuild the resource index and SLQ db. The Solr index also needs to be rebuilt or updated.

The script assumes Fedora objects with metadata in DC and CMDI as inline XML embedded in the FOXML. Different find/replace patterns may be needed for other metadata in case they include Fedora PIDs.
