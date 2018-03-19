/*
 * Copyright (c) 2007, Swedish Institute of Computer Science.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the Institute nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * This file is part of the Contiki operating system.
 *
 */

/**
 * \file
 *         Reliable single-hop unicast example
 * \author
 *         Adam Dunkels <adam@sics.se>
 */

#include <stdio.h>

// #include <stdint.h>

#include "contiki.h"
#include "net/rime/rime.h"

#include "lib/list.h"
#include "lib/memb.h"


// #include "random.h"
#include "board-peripherals.h"

// #include "dev/button-sensor.h"
// #include "dev/leds.h"

#define MAX_RETRANSMISSIONS 4
#define NUM_HISTORY_ENTRIES 4
#define EXT_FLASH_BASE_ADDR_SENSOR_DATA       0 
#define EXT_FLASH_MEMORY_END_ADDRESS          0x400010 // 4194320B
#define EXT_FLASH_BASE_ADDR       0
#define EXT_FLASH_SIZE            4*1024*1024
#define RECEIVER_ID_1         235
#define RECEIVER_ID_2         137 // 137
#define SENDSIZE              4
/*---------------------------------------------------------------------------*/
PROCESS(test_runicast_process, "runicast test");
AUTOSTART_PROCESSES(&test_runicast_process);
/*---------------------------------------------------------------------------*/
/* OPTIONAL: Sender history.
 * Detects duplicate callbacks at receiving nodes.
 * Duplicates appear when ack messages are lost. */
struct history_entry {
  struct history_entry *next;
  linkaddr_t addr;
  uint8_t seq;
};
LIST(history_table);
MEMB(history_mem, struct history_entry, NUM_HISTORY_ENTRIES);
/*---------------------------------------------------------------------------*/
static void
recv_runicast(struct runicast_conn *c, const linkaddr_t *from, uint8_t seqno)
{
  /* OPTIONAL: Sender history */
  struct history_entry *e = NULL;
  for(e = list_head(history_table); e != NULL; e = e->next) {
    if(linkaddr_cmp(&e->addr, from)) {
      break;
    }
  }
  if(e == NULL) {
    /* Create new history entry */
    e = memb_alloc(&history_mem);
    if(e == NULL) {
      e = list_chop(history_table); /* Remove oldest at full history */
    }
    linkaddr_copy(&e->addr, from);
    e->seq = seqno;
    list_push(history_table, e);
  } else {
    /* Detect duplicate callback */
    if(e->seq == seqno) {
      printf("runicast message received from %d.%d, seqno %d (DUPLICATE)\n",
	     from->u8[0], from->u8[1], seqno);
      return;
    }
    /* Update existing history entry */
    e->seq = seqno;
  }

  printf("runicast message received from %d.%d, seqno %d, data: %s\n",
	 from->u8[0], from->u8[1], seqno, (char *)packetbuf_dataptr());
  
}
static void
sent_runicast(struct runicast_conn *c, const linkaddr_t *to, uint8_t retransmissions)
{
  printf("runicast message sent to %d.%d, retransmissions %d\n",
	 to->u8[0], to->u8[1], retransmissions);
}
static void
timedout_runicast(struct runicast_conn *c, const linkaddr_t *to, uint8_t retransmissions)
{
  printf("runicast message timed out when sending to %d.%d, retransmissions %d\n",
	 to->u8[0], to->u8[1], retransmissions);
}
static const struct runicast_callbacks runicast_callbacks = {recv_runicast,
							     sent_runicast,
							     timedout_runicast};
static struct runicast_conn runicast;
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(test_runicast_process, ev, data)
{
  PROCESS_EXITHANDLER(runicast_close(&runicast);)

  PROCESS_BEGIN();

  runicast_open(&runicast, 144, &runicast_callbacks);

  // .2 add receiver print data
  // .3 add read from ext, .1 fix new line .2 debug s output
  printf("Begin: 0.3.1\n"); 

  /* OPTIONAL: Sender history */
  list_init(history_table);
  memb_init(&history_mem);

  /* Receiver node: do nothing */
  if(linkaddr_node_addr.u8[0] == RECEIVER_ID_1 &&
     linkaddr_node_addr.u8[1] == RECEIVER_ID_2) {
    PROCESS_WAIT_EVENT_UNTIL(0);
  }


  // data fill
  if (!ext_flash_open()) {
    printf("Failed to open flash??\n");
  }
  // end data fill
  // ext_flash_erase(EXT_FLASH_BASE_ADDR, 3000);
  
  // Create 32KB worth of data
  int length = 300; // 32 * 1024;
  uint8_t data[300];
  // for (int i = 0; i < length; i+= 4) {
  //   data[0] = i % 256;
  //   data[1] = (i + 1) % 256;
  //   data[2] = (i + 2) % 256;
  //   data[3] = (i + 3) % 256;
  //   if (ext_flash_write(i, 4, (uint8_t *)&data)) {
  //     printf("%d %d %d %d\n", data[0], data[1], data[2], data[3]);
  //   }
  // }
  // end data fill
  // for (int i = 0; i < length; i+= 4) {
    if(ext_flash_read(0, 300, (uint8_t *)&data))
      printf("%d %d %d %d\n", data[0], data[1], data[2], data[3]);
  // }

  printf("%s\n", linkaddr_node_addr.u8[0]);
  printf("%s\n", linkaddr_node_addr.u8[1]);

  int sendLoc = 0;
  while(1) {
    static struct etimer et;

    etimer_set(&et, 1*CLOCK_SECOND);
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));

    if(!runicast_is_transmitting(&runicast)) {
      linkaddr_t recv;

      
      // ext_flash_read(sendLoc, 4, (uint8_t *)&data);
      // sendLoc = sendLoc + 4;
      // printf("%d\n", sendLoc);
      printf("%d %d %d %d\n", data[0], data[1], data[2], data[3]);
      packetbuf_copyfrom("data", 4);
      recv.u8[0] = RECEIVER_ID_1;
      recv.u8[1] = RECEIVER_ID_2;

      printf("%u.%u: sending runicast to address %u.%u\n",
	     linkaddr_node_addr.u8[0],
	     linkaddr_node_addr.u8[1],
	     recv.u8[0],
	     recv.u8[1]);

      runicast_send(&runicast, &recv, MAX_RETRANSMISSIONS);
    }
  }

  PROCESS_END();
}
/*---------------------------------------------------------------------------*/
