hw1 -> 
  xfer 32KB data to node 11265
  check data xfered correctness
    - process output, compare data for 32KB
    - do diff

hw2 -> of 655 xmissions (discard first since it is the polling xfer)
  xfer 32KB data to node 11265 @ CHNL 11 @ 50B/p   // 793 transmissions 
  xfer 32KB data to node 11265 @ CHNL 18 @ 50B/p   // 779 transmissions
  xfer 32KB data to node 11265 @ CHNL 24 @ 50B/p   // 697 transmissions

  xfer 32KB data to node 11265 @ CHNL 24 @ 10B/p
  xfer 32KB data to node 11265 @ CHNL 24 @ 100B/p