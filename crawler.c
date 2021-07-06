#include <dirent.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <stdbool.h>

static uint64_t l_to_b(const uint64_t n) {
  uint64_t accum = 0;
  uint8_t *raw = (uint8_t *)&n;
  int p;
  for (p = 0; p < 8; p++) {
    accum = (accum << 8) + raw[p];
  }
  return accum;
}



typedef struct {
  int *array;
  size_t used;
  size_t size;
//  int *brray;
//  size_t bsed;
//  size_t bize;
  

} Array;

void initArray(Array *a, size_t initialSize) {
  a->array = malloc(initialSize * sizeof(int));
  a->used = 0;
  a->size = initialSize;
}

void insertArray(Array *a, int element) {
  // a->used is the number of used entries, because a->array[a->used++] updates a->used only *after* the array has been accessed.
  // Therefore a->used can go up to a->size 
  if (a->used == a->size) {
    a->size += 1;
    a->array = realloc(a->array, a->size * sizeof(int));
  }
  a->array[a->used++] = element;
}

void freeArray(Array *a) {
  free(a->array);
  a->array = NULL;
  a->used = a->size = 0;
}

//void initBrray(Array *b, size_t initialBize) {
//  b->brray = malloc(initialBize * sizeof(int));
//  b->bsed = 0;
//  b->bize = initialBize;
//}
//
//void insertBrray(Array *b, uint64_t* element) {
//  // a->used is the number of used entries, because a->array[a->used++] updates a->used only *after* the array has been accessed.
//  // Therefore a->used can go up to a->size 
//  if (b->bsed == b->bize) {
//    b->bize += 1;
//    b->brray = realloc(b->brray, b->bize * sizeof(uint64_t*));
//  }
//  b->brray[b->bsed++] = *element;
//}
//
//void freeBrray(Array *b) {
//  free(b->brray);
//  b->brray = NULL;
//  b->bsed = b->bize = 0;
//}















long int findSize(char file_name[])
{
    FILE* s = fopen(file_name, "r");

    if (s == NULL) {
        printf("File Not Found!\n");
        return -1;
    }

    fseek(s, 0L, SEEK_END);

    long int res = ftell(s);

    fclose(s);

    return res;
}



#define HDR_START 20
//#define int volume_off[] {'20', 


int main(int argc, char *argv[]) {

        Array a;
 //       Array b;
        initArray(&a, 0);
//        initBrray(&b, 0);
        int minnified = 0;
        int index_compressed = 0;
        int full_sized = 0;
        int v;
        int y;
        int i;
        int t;
        uint64_t q;
        int off;
        FILE *sketch;
        long int size = findSize(argv[i]);
        uint64_t offset[58];
        int vol_off[29];
//        uint8_t
//        char *

      for ( i = 1; i < argc; i++) { 

          sketch = fopen(argv[i], "r");

          fseek(sketch, 160, SEEK_SET);

          l_to_b(fread(&offset, 8, 59, sketch));

          //subtract 20 from volumetrics array because the read starts at section #20 in the header

          for (y = 0; y < 59; y++)   {

             if (y == 1 || y == 4 || y == 6 || y == 8 || y == 10 || y == 12 || y == 14 || y == 15 || y == 16 || y == 17 || y == 18 || y == 19 || y == 21 || y == 23 ||
                 y == 25 || y == 27 || y == 29 || y == 31 || y == 33 || y == 35 || y == 37 || y == 39 || y == 44 || y == 46 || y == 48 || y == 50 || y == 52 || y == 54 ||
                 y == 56 || y == 58) {
                continue;
           }else{ 

                 if (l_to_b(offset[y]) > 0)
                 insertArray(&a, l_to_b(offset[y]));
             }
         
          }
         
        uint64_t *minn = malloc(4);
        uint64_t *index = malloc(4);
          
        uint64_t table;
         
          for (t = 0; t < a.used; t++){

              fseek(sketch, a.array[t] + 8, SEEK_SET);
              l_to_b(fread(&table, 4, 1, sketch));

              for ( q = 0; q < 32; q++){
  
                  if (table & (1 << q)){

                     minnified = minnified + 1;
                     break; 
                     }

               }
              

//              all_tables[t] = table;
 //            printf("table %lu\n", table);
//              free(table);
          }


       }
             printf("table %i\n", minnified);

  }

