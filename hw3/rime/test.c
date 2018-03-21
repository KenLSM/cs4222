#include <stdio.h>
#include <stdint.h>
#include <string.h>

int main(int argc, char** argv) {

  uint8_t input[1200];
  memset(input, '\0', sizeof(input));
  for(int i = 0; i < 1100; i+=3) {
    char int_gen_buff[3];
    sprintf(int_gen_buff, "%02d", i % 100);
    input[i] = int_gen_buff[0];
    input[i + 1] = int_gen_buff[1];
    input[i + 2] = ',';
    // printf("%c\n", input[i]);
  }
  // input[10] = '\0';

  printf("\n", strlen(input));
  printf("|%s| %d\n", input, strlen(input));
  return 0;
}