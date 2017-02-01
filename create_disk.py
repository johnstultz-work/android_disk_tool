#!/usr/bin/python

import sys, getopt
import os

disk_name = "disk.raw"
MBR_SIZE = 1024*1024

class partition():
	name = ''
	size = 0
	ptype = ""


def partition_disk(partitions):
	cmd = "parted "+disk_name+" --script mklabel msdos"
	os.system(cmd)

	start = MBR_SIZE
	for p in partitions:
		cmd = "parted "+disk_name+ " --script mkpart primary "+ p.ptype +" "+ str(start)+"B " + str(start+p.size-1)+ "B "
		print cmd
		os.system(cmd)
		start += p.size

	cmd = "parted "+disk_name+" set 1 boot on"
	os.system(cmd)


def add_bootloader():
	cmd = "dd conv=notrunc bs=440 count=1 if=/usr/lib/SYSLINUX/mbr.bin of=" + disk_name
	os.system(cmd)

	cmd = "syslinux -i -t "+str(MBR_SIZE) + " " + disk_name
	os.system(cmd)


def create_disk(partitions):
	cmd = "dd if=/dev/zero of=MBR bs="+str(MBR_SIZE) +" count=1"
	os.system(cmd)

	size = MBR_SIZE
	names = "MBR "
	for p in partitions:
		names += p.name +" "
		size += p.size

	cmd = "cat " + names + "> "+ disk_name
	os.system(cmd)

	cmd = "rm MBR"
	os.system(cmd)	


def calculate_partitions(img_pairs):
	partitions = []
	for (f,t) in img_pairs:
		p = partition()
		statinfo = os.stat(f)
		p.name = f
		p.size = statinfo.st_size
		p.ptype = t
		partitions.append(p)
	return partitions


def generate_boot(fname, kernel, ramdisk, syslinux):
	cmd = "dd if=/dev/zero of="+fname+" bs=100M count=1"
	os.system(cmd)

	cmd = "mkfs.fat "+fname
	os.system(cmd)

	cmd = "mcopy -i "+fname+" "+kernel+" ::/"
	os.system(cmd)

	cmd = "mcopy -i "+fname+" "+ramdisk+" ::/"
	os.system(cmd)

	cmd = "mcopy -i "+fname+" "+syslinux+" ::/"
	os.system(cmd)


def generate_ext4(label, size):
	cmd = "fallocate -l "+size+" "+label+".img"
	os.system(cmd)

	cmd = "mkfs.ext4 "+label+".img -L "+label
	os.system(cmd)


HELP_TXT="create_disk.py -k <kernel> -r <ramdisk> -s <system img>"
def main(argv):
	kernel=""
	initrd = ""
	system = ""

	try:
		opts, args = getopt.getopt(argv,"hk:r:s:")
	except getopt.GetoptError:
		print HELP_TXT
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print HELP_TXT
			sys.exit()
		elif opt in ("-k"):
			kernel = arg
		elif opt in ("-r"):
			ramdisk = arg
		elif opt in ("-s"):
			system = arg

	# generate partition files
	generate_boot("dos.img", kernel, ramdisk, "syslinux.cfg")
	generate_ext4("cache", "2G")
	generate_ext4("data", "4G")

	cmd = "simg2img "+system+" system.img.raw"
	os.system(cmd)


	#Create disk, partition and add bootloader
	files = [("dos.img", "fat32"), ("system.img.raw","ext4"), ("cache.img","ext4"), ("data.img", "ext4")]
	partitions = calculate_partitions(files)
	create_disk(partitions)
	partition_disk(partitions)
	add_bootloader()

	# cleanup
	cmd = "rm dos.img cache.img data.img system.img.raw"
	os.system(cmd)



if __name__ == "__main__":
   main(sys.argv[1:])


