---
title: "Hypervisor Basics"
category: "operating-systems"
difficulty: "advanced"
tags: [virtualization, kvm, hypervisor]
related: [minimal-kernel, virtual-memory-paging, bootloader]
---

# Hypervisor Basics

A hypervisor runs entire virtual machines: it uses CPU virtualization extensions to let a guest OS execute directly on hardware while trapping privileged operations. Building on KVM yourself teaches you how VMs really work — VM exits, virtual CPUs, and why virtualization is close to native speed.

## Core concepts

- **Type 1 vs type 2 hypervisors** — Type 1 (bare metal: ESXi, Hyper-V, Xen) runs directly on hardware; type 2 (hosted: KVM, VirtualBox) runs inside a host OS. KVM is technically type 1-ish: it turns the Linux kernel itself into the hypervisor.
- **Hardware virtualization (VT-x/AMD-V)** — CPU extensions add a "guest mode" with its own VMCS/VMCB control structure. Most guest instructions run natively; privileged ones trap to the hypervisor (a "VM exit").
- **KVM's architecture** — KVM is a Linux kernel module exposing `/dev/kvm`. Userspace (QEMU) uses ioctls to create VMs, vCPUs, and memory slots; the kernel module handles the actual guest execution.
- **VM exits and the exit handler** — When the guest does something privileged (I/O port access, halt, page-table change), the CPU exits to the hypervisor with an exit reason. The hypervisor emulates the operation and resumes the guest.
- **Memory virtualization** — Guest-physical addresses map to host-virtual addresses via a second layer of page tables (EPT on Intel, NPT/RVI on AMD), so the guest's MMU works unmodified while the host stays in control.
- **Virtio paravirtualization** — Instead of emulating slow real hardware, virtio defines simple virtual devices (net, block) with shared-memory queues (vrings). Guests use virtio drivers for near-native I/O speed.
- **Interrupt virtualization** — The hypervisor injects virtual interrupts into the guest (via the LAPIC emulation or posted interrupts) so guest drivers see hardware-like behavior.

## How it works

Your userspace program opens `/dev/kvm`, issues `KVM_CREATE_VM`, and registers guest memory with `KVM_SET_USER_MEMORY_REGION` (a chunk of your own `mmap`'d memory becomes guest RAM at guest-physical address 0). It creates a vCPU (`KVM_CREATE_VCPU`), `mmap`s the shared `kvm_run` struct, and loads a tiny guest binary (16-bit or 64-bit) at the guest's reset vector. Then it loops on `KVM_RUN`: the kernel module executes the guest natively until a VM exit occurs — e.g. the guest does port I/O to print a character — and returns the exit reason. Your program emulates the device (writes the char to stdout), advances the guest's instruction pointer past the trapped instruction, and calls `KVM_RUN` again. The guest believes it's alone on the hardware; in reality every privileged act is intercepted and emulated.

## Build milestones

1. Write a ~200-line KVM "hello world": create a VM, load a 16-bit guest that writes to a port, handle `KVM_EXIT_IO` exits in the loop, and print the guest's output.
2. Add a virtual serial device: emulate enough of a 16550 UART via IO exits that the guest can run a real serial driver.
3. Implement guest memory properly: multiple memory slots, and handle `KVM_EXIT_MMIO` for memory-mapped device emulation.
4. Boot a real payload: load a Linux bzImage or a multiboot kernel as the guest and get it to userspace.
5. Add a virtio-net device with a vring queue pair, bridging guest packets to a TAP interface on the host.
6. Support SMP: run 2+ vCPUs on host threads, handle IPIs, and boot an SMP-aware guest kernel.

## Best resources

- [KVM API documentation](https://www.kernel.org/doc/html/latest/virt/kvm/api.html) — the complete ioctl reference; your primary spec.
- [A simple KVM hypervisor example (David Xie)](https://david942j.blogspot.com/2018/10/note-learning-kvm-implement-your-own.html) — a well-explained minimal hypervisor walkthrough.
- [kvmtool (lkvm)](https://github.com/kvmtool/kvmtool) — a minimal VMM in ~10k lines; far more readable than QEMU for learning.
- [QEMU documentation — KVM](https://www.qemu.org/docs/master/system/introduction.html) — how the production VMM uses KVM underneath.
- [Intel SDM Volume 3C, Chapters 24–33](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html) — VMX operation: VMCS fields, exits, and entry, from the source.
- [AMD64 APM Volume 2, Chapter 15 (SVM)](https://www.amd.com/en/support/tech-docs.html) — AMD's virtualization architecture for the other half of the story.
- [virtio specification](https://docs.oasis-open.org/virtio/virtio/v1.3/virtio-v1.3.html) — the paravirtual device standard.

## Stretch ideas

- Implement live migration: copy guest memory to another host while the VM runs, tracking dirty pages with KVM's dirty logging.
- Add nested virtualization support and run your hypervisor inside itself.
