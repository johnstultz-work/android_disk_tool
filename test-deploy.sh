#!/bin/bash

while [[ $# -gt 1 ]]
do
key="$1"

case $key in
	-b|--bucket)
	BUCKET="$2"
	shift # past argument
	;;
	*)
		# unknown option
	;;
esac
shift # past argument or value
done

if [[ -z "${BUCKET}" ]]; then
	echo "No project specified, please use -b <bucketname>"
	echo "Likely bucket names:"
	gsutil ls | sed -e 's/gs:\/\///' | sed -e 's/\///'
	exit
fi

echo BUCKET = "${BUCKET}"


NOW=$(date +%d-%m-%Y-%s)
DISKIMG=disk-$NOW.tar.gz
IMGNAME=android-img-$NOW


tar -Sczf $DISKIMG disk.raw

gsutil cp $DISKIMG  gs://$BUCKET/
gcloud compute images create "$IMGNAME" \
	--source-uri "https://storage.googleapis.com/$BUCKET/$DISKIMG"
gcloud compute instances create "android-$NOW" --machine-type "custom-1-1024" --image "$IMGNAME"

# Spawn and setup CTS test runner
# gcloud compute instances create "cts-test-runner-$NOW" --machine-type "n1-standard-1" --image "cos-stable-56-9000-84-2" --image-project "cos-cloud" --boot-disk-size "20"
#
#### <ssh to cts-test-runner> ###
# $ docker build -t cts https://raw.githubusercontent.com/johnstultz-work/dockerstuff/master/Dockerfile.cts
# $ docker run -t -i cts
#
#### now in running docker image ####
# $ cd
# $ unzip android-cts-7.1_r1-linux_x86-x86.zip
# $ cd android-cts/tools
# $ adb connect <ip for android instance>
# $ ./cts-tradefed
# cts-tf > run cts


