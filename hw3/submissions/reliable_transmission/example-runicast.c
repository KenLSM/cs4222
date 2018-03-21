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

#define MAX_RETRANSMISSIONS 20
#define NUM_HISTORY_ENTRIES 20
#define EXT_FLASH_BASE_ADDR_SENSOR_DATA       0 
#define EXT_FLASH_MEMORY_END_ADDRESS          0x400010 // 4194320B
#define EXT_FLASH_BASE_ADDR       0
#define EXT_FLASH_SIZE            4*1024*1024
#define RECEIVER_ID_1         44
#define RECEIVER_ID_2         1 // 137
#define DATA_SIZE             32 * 1024 // total file size: 32KB
#define DATA_SEND_SIZE        100
#define BUFF_SIZE             DATA_SEND_SIZE * 1
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
static int data_next = 0;
static uint8_t input_data_buf[BUFF_SIZE + 1];
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
  // uint8_t* buf = (uint8_t *)packetbuf_dataptr();
  // packetbuf_copyto(4, buf);
  static uint8_t buf[BUFF_SIZE + 1];
  memset(buf, '\0', sizeof(buf));
  strcpy(buf, packetbuf_dataptr());
  printf("runicast message received from %d.%d, seqno %d, data: %s length: %d\n",
   from->u8[0], from->u8[1], seqno, (uint8_t *)buf, strlen(buf));
	 // from->u8[0], from->u8[1], seqno, buf[0], buf[1], buf[2], buf[3], sizeof(buf));
  
}
static void
sent_runicast(struct runicast_conn *c, const linkaddr_t *to, uint8_t retransmissions)
{

  data_next += DATA_SEND_SIZE;
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
  // .3 add read from ext, .1 fix new line .2 debug s output .3 char sprintf
  // .4 data_next
  // .5 section by 1024
  // .6 char everything (1byte) .1 increase charv 1
  printf("Begin: 0.6\n"); 

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
    printf("Failed to open flash!!\n");
  }
  ext_flash_erase(EXT_FLASH_BASE_ADDR, DATA_SIZE);
  
  // Create DATA_SIZE worth of data

  for (int i = 0; i < DATA_SIZE; i+= 3) {
    static char gen_buf[3];
    sprintf(gen_buf, "%02d", i % 100);
    input_data_buf[0] = gen_buf[0];
    input_data_buf[1] = gen_buf[1];
    input_data_buf[2] = ',';
    if (ext_flash_write(i, 3, (uint8_t *)&input_data_buf)) { // write 4 bytes
      printf("%d %d %d %d %d\n", i, input_data_buf[0], input_data_buf[1], input_data_buf[2]);
    }
  }
  // end data fill
  for (int i = 0; i < DATA_SIZE; i+= BUFF_SIZE) {
    if(ext_flash_read(i, BUFF_SIZE, (uint8_t *)&input_data_buf))  // test read 100 bytes
      printf("%s\n", input_data_buf);
  }
  ext_flash_close();

  while(1) {
    static struct etimer et;

    etimer_set(&et, CLOCK_SECOND / 2);
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));

    if(!runicast_is_transmitting(&runicast)) {
      linkaddr_t recv;

      if (data_next > DATA_SIZE) {
        printf("DATA SEND COMPLETE: %d of %d\n", data_next, DATA_SIZE);
        break;
      }

      if (data_next % BUFF_SIZE == 0) {
        ext_flash_open();
        memset(input_data_buf, '\0', sizeof(input_data_buf)); // reset to empty
        if (ext_flash_read(data_next, BUFF_SIZE, (uint8_t *)&input_data_buf)) {
          printf("DATA READ PASS: %d %s\n", data_next, input_data_buf);
        } else {
          printf("DATA READ FAIL: %d %d\n", data_next, BUFF_SIZE);
        }
        ext_flash_close();
      }

      packetbuf_copyfrom(input_data_buf, BUFF_SIZE + 1);
      printf("DATA SEND: %d of %d | Contents: %s\n", data_next, DATA_SIZE, input_data_buf);

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
