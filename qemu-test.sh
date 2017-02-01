qemu-system-x86_64 \
	-enable-kvm \
	-m 1G \
	-smp 4 \
	-hda disk.raw \
	-nographic \
	-serial mon:stdio  \
	-nodefaults \
	-vnc :0 \
	-device VGA \
	-netdev user,id=mynet,hostfwd=tcp::5400-:5555 -device virtio-net-pci,netdev=mynet \
	-device virtio-mouse-pci -device virtio-keyboard-pci \

