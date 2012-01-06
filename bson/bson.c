/* bson.c */

/*    Copyright 2009, 2010 10gen Inc.
 *
 *    Licensed under the Apache License, Version 2.0 (the "License");
 *    you may not use this file except in compliance with the License.
 *    You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 *    Unless required by applicable law or agreed to in writing, software
 *    distributed under the License is distributed on an "AS IS" BASIS,
 *    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *    See the License for the specific language governing permissions and
 *    limitations under the License.
 */

#include "bson.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>

const int initialBufferSize = 128;

/* only need one of these */
static const int zero = 0;

/* ----------------------------
   READING
   ------------------------------ */

bson * bson_empty(bson * obj){
    static char * data = "\005\0\0\0\0";
    return bson_init(obj, data, 0);
}

int bson_copy(bson* out, const bson* in){
    if (!out) return 0;
    out->data = bson_malloc(bson_size(in));
    if (!out->data) return 0;
    out->owned = 1;
    memcpy(out->data, in->data, bson_size(in));
    return 1;
}

bson * bson_from_buffer(bson * b, bson_buffer * buf){
    return bson_init(b, bson_buffer_finish(buf), 1);
}

bson * bson_init( bson * b , char * data , bson_bool_t mine ){
    b->data = data;
    b->owned = mine;
    return b;
}

bson * bson_init_safe( bson * b , char * data , bson_bool_t mine , size_t buflen ) {
    b->data = data;
    b->owned = mine;

    if (buflen < 5)
        return 0;

    if (bson_size(b) > buflen)
        return 0;

    return b;
}

int bson_size(const bson * b ){
    int i;
    if ( ! b || ! b->data )
        return 0;
    bson_little_endian32(&i, b->data);
    return i;
}
void bson_destroy( bson * b ){
    if ( b->owned && b->data )
        free( b->data );
    b->data = 0;
    b->owned = 0;
}

static char hexbyte(char hex){
    switch (hex){
        case '0': return 0x0;
        case '1': return 0x1;
        case '2': return 0x2;
        case '3': return 0x3;
        case '4': return 0x4;
        case '5': return 0x5;
        case '6': return 0x6;
        case '7': return 0x7;
        case '8': return 0x8;
        case '9': return 0x9;
        case 'a': 
        case 'A': return 0xa;
        case 'b':
        case 'B': return 0xb;
        case 'c':
        case 'C': return 0xc;
        case 'd':
        case 'D': return 0xd;
        case 'e':
        case 'E': return 0xe;
        case 'f':
        case 'F': return 0xf;
        default: return 0x0; /* something smarter? */
    }
}

void bson_oid_from_string(bson_oid_t* oid, const char* str){
    int i;
    for (i=0; i<12; i++){
        oid->bytes[i] = (hexbyte(str[2*i]) << 4) | hexbyte(str[2*i + 1]);
    }
}
void bson_oid_to_string(const bson_oid_t* oid, char* str){
    static const char hex[16] = {'0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'};
    int i;
    for (i=0; i<12; i++){
        str[2*i]     = hex[(oid->bytes[i] & 0xf0) >> 4];
        str[2*i + 1] = hex[ oid->bytes[i] & 0x0f      ];
    }
    str[24] = '\0';
}
void bson_oid_gen(bson_oid_t* oid){
    static int incr = 0;
    static int fuzz = 0;
    int i = incr++; /*TODO make atomic*/
    int t = time(NULL);

    /* TODO rand sucks. find something better */
    if (!fuzz){
        srand(t);
        fuzz = rand();
    }
    
    bson_big_endian32(&oid->ints[0], &t);
    oid->ints[1] = fuzz;
    bson_big_endian32(&oid->ints[2], &i);
}

time_t bson_oid_generated_time(bson_oid_t* oid){
    time_t out;
    bson_big_endian32(&out, &oid->ints[0]);
    return out;
}

void bson_print( bson * b ){
    bson_print_raw( b->data , 0 );
}

void bson_print_raw( const char * data , int depth ){
    bson_iterator i;
    const char * key;
    int temp;
    char oidhex[25];
    bson_iterator_init( &i , data );

    while ( bson_iterator_next( &i ) ){
        bson_type t = bson_iterator_type( &i );
        if ( t == 0 )
            break;
        key = bson_iterator_key( &i );
        
        for ( temp=0; temp<=depth; temp++ )
            printf( "\t" );
        printf( "%s : %d \t " , key , t );
        switch ( t ){
        case bson_int: printf( "%d" , bson_iterator_int( &i ) ); break;
        case bson_double: printf( "%f" , bson_iterator_double( &i ) ); break;
        case bson_bool: printf( "%s" , bson_iterator_bool( &i ) ? "true" : "false" ); break;
        case bson_string: printf( "%s" , bson_iterator_string( &i ) ); break;
        case bson_null: printf( "null" ); break;
        case bson_oid: bson_oid_to_string(bson_iterator_oid(&i), oidhex); printf( "%s" , oidhex ); break;
        case bson_object:
        case bson_array:
            printf( "\n" );
            bson_print_raw( bson_iterator_value( &i ) , depth + 1 );
            break;
        default:
            fprintf( stderr , "can't print type : %d\n" , t );
        }
        printf( "\n" );
    }
}

/* ----------------------------
   ITERATOR
   ------------------------------ */

void bson_iterator_init( bson_iterator * i , const char * bson ){
    i->cur = bson + 4;
    i->first = 1;
}

bson_type bson_find(bson_iterator* it, const bson* obj, const char* name){
    bson_iterator_init(it, obj->data);
    while(bson_iterator_next(it)){
        if (strcmp(name, bson_iterator_key(it)) == 0)
            break;
    }
    return bson_iterator_type(it);
}

bson_bool_t bson_iterator_more( const bson_iterator * i ){
    return *(i->cur);
}

bson_type bson_iterator_next( bson_iterator * i ){
    int ds;

    if ( i->first ){
        i->first = 0;
        return (bson_type)(*i->cur);
    }
    
    switch ( bson_iterator_type(i) ){
    case bson_eoo: return bson_eoo; /* don't advance */
    case bson_undefined:
    case bson_null: ds = 0; break;
    case bson_bool: ds = 1; break;
    case bson_int: ds = 4; break;
    case bson_long:
    case bson_double:
    case bson_timestamp:
    case bson_date: ds = 8; break;
    case bson_oid: ds = 12; break;
    case bson_string:
    case bson_symbol:
    case bson_code: ds = 4 + bson_iterator_int_raw(i); break;
    case bson_bindata: ds = 5 + bson_iterator_int_raw(i); break;
    case bson_object:
    case bson_array:
    case bson_codewscope: ds = bson_iterator_int_raw(i); break;
    case bson_dbref: ds = 4+12 + bson_iterator_int_raw(i); break;
    case bson_regex:
        {
            const char * s = bson_iterator_value(i);
            const char * p = s;
            p += strlen(p)+1;
            p += strlen(p)+1;
            ds = p-s;
            break;
        }

    default: 
        {
            char msg[] = "unknown type: 000000000000";
            bson_numstr(msg+14, (unsigned)(i->cur[0]));
            bson_fatal_msg(0, msg);
            return bson_error;
        }
    }
    
    i->cur += 1 + strlen( i->cur + 1 ) + 1 + ds;

    return (bson_type)(*i->cur);
}

bson_type bson_iterator_type( const bson_iterator * i ){
    return (bson_type)i->cur[0];
}
const char * bson_iterator_key( const bson_iterator * i ){
    return i->cur + 1;
}
const char * bson_iterator_value( const bson_iterator * i ){
    const char * t = i->cur + 1;
    t += strlen( t ) + 1;
    return t;
}

/* types */

int bson_iterator_int_raw( const bson_iterator * i ){
    int out;
    bson_little_endian32(&out, bson_iterator_value( i ));
    return out;
}
double bson_iterator_double_raw( const bson_iterator * i ){
    double out;
    bson_little_endian64(&out, bson_iterator_value( i ));
    return out;
}
int64_t bson_iterator_long_raw( const bson_iterator * i ){
    int64_t out;
    bson_little_endian64(&out, bson_iterator_value( i ));
    return out;
}

bson_bool_t bson_iterator_bool_raw( const bson_iterator * i ){
    return bson_iterator_value( i )[0];
}

bson_oid_t * bson_iterator_oid( const bson_iterator * i ){
    return (bson_oid_t*)bson_iterator_value(i);
}

int bson_iterator_int( const bson_iterator * i ){
    switch (bson_iterator_type(i)){
        case bson_int: return bson_iterator_int_raw(i);
        case bson_long: return bson_iterator_long_raw(i);
        case bson_double: return bson_iterator_double_raw(i);
        default: return 0;
    }
}
double bson_iterator_double( const bson_iterator * i ){
    switch (bson_iterator_type(i)){
        case bson_int: return bson_iterator_int_raw(i);
        case bson_long: return bson_iterator_long_raw(i);
        case bson_double: return bson_iterator_double_raw(i);
        default: return 0;
    }
}
int64_t bson_iterator_long( const bson_iterator * i ){
    switch (bson_iterator_type(i)){
        case bson_int: return bson_iterator_int_raw(i);
        case bson_long: return bson_iterator_long_raw(i);
        case bson_double: return bson_iterator_double_raw(i);
        default: return 0;
    }
}

bson_bool_t bson_iterator_bool( const bson_iterator * i ){
    switch (bson_iterator_type(i)){
        case bson_bool: return bson_iterator_bool_raw(i);
        case bson_int: return bson_iterator_int_raw(i) != 0;
        case bson_long: return bson_iterator_long_raw(i) != 0;
        case bson_double: return bson_iterator_double_raw(i) != 0;
        case bson_eoo:
        case bson_null: return 0;
        default: return 1;
    }
}

const char * bson_iterator_string( const bson_iterator * i ){
    return bson_iterator_value( i ) + 4;
}
int bson_iterator_string_len( const bson_iterator * i ){
    return bson_iterator_int_raw( i );
}

const char * bson_iterator_code( const bson_iterator * i ){
    switch (bson_iterator_type(i)){
        case bson_string:
        case bson_code: return bson_iterator_value(i) + 4;
        case bson_codewscope: return bson_iterator_value(i) + 8;
        default: return NULL;
    }
}

void bson_iterator_code_scope(const bson_iterator * i, bson * scope){
    if (bson_iterator_type(i) == bson_codewscope){
        int code_len;
        bson_little_endian32(&code_len, bson_iterator_value(i)+4);
        bson_init(scope, (void*)(bson_iterator_value(i)+8+code_len), 0);
    }else{
        bson_empty(scope);
    }
}

bson_date_t bson_iterator_date(const bson_iterator * i){
    return bson_iterator_long_raw(i);
}

time_t bson_iterator_time_t(const bson_iterator * i){
    return bson_iterator_date(i) / 1000;
}

int bson_iterator_bin_len( const bson_iterator * i ){
    return bson_iterator_int_raw( i );
}

char bson_iterator_bin_type( const bson_iterator * i ){
    return bson_iterator_value(i)[4];
}
const char * bson_iterator_bin_data( const bson_iterator * i ){
    return bson_iterator_value( i ) + 5;
}

const char * bson_iterator_regex( const bson_iterator * i ){
    return bson_iterator_value( i );
}
const char * bson_iterator_regex_opts( const bson_iterator * i ){
    const char* p = bson_iterator_value( i );
    return p + strlen(p) + 1;

}

void bson_iterator_subobject(const bson_iterator * i, bson * sub){
    bson_init(sub, (char*)bson_iterator_value(i), 0);
}
void bson_iterator_subiterator(const bson_iterator * i, bson_iterator * sub){
    bson_iterator_init(sub, bson_iterator_value(i));
}

/* ----------------------------
   BUILDING
   ------------------------------ */

bson_buffer * bson_buffer_init( bson_buffer * b ){
    b->buf = (char*)bson_malloc( initialBufferSize );
    if (!b->buf)
        return 0;

    b->bufSize = initialBufferSize;
    b->cur = b->buf + 4;
    b->finished = 0;
    b->stackPos = 0;
    return b;
}

void bson_append_byte( bson_buffer * b , char c ){
    b->cur[0] = c;
    b->cur++;
}
void bson_append( bson_buffer * b , const void * data , int len ){
    memcpy( b->cur , data , len );
    b->cur += len;
}
void bson_append32(bson_buffer * b, const void * data){
    bson_little_endian32(b->cur, data);
    b->cur += 4;
}
void bson_append64(bson_buffer * b, const void * data){
    bson_little_endian64(b->cur, data);
    b->cur += 8;
}

bson_buffer * bson_ensure_space( bson_buffer * b , const int bytesNeeded ){
    int pos = b->cur - b->buf;
    char * orig = b->buf;
    int new_size;

    if (b->finished) {
        bson_fatal_msg(!!b->buf, "trying to append to finished buffer");
        return NULL;
    }

    if (pos + bytesNeeded <= b->bufSize)
        return b;

    new_size = 1.5 * (b->bufSize + bytesNeeded);
    b->buf = realloc(b->buf, new_size);
    if (!b->buf) {
        bson_fatal_msg(!!b->buf, "realloc() failed");
        return NULL;
    }

    b->bufSize = new_size;
    b->cur += b->buf - orig;

    return b;
}

char * bson_buffer_finish( bson_buffer * b ){
    int i;
    if ( ! b->finished ){
        if ( ! bson_ensure_space( b , 1 ) ) return 0;
        bson_append_byte( b , 0 );
        i = b->cur - b->buf;
        bson_little_endian32(b->buf, &i);
        b->finished = 1;
    }
    return b->buf;
}

void bson_buffer_destroy( bson_buffer * b ){
    free( b->buf );
    b->buf = 0;
    b->cur = 0;
    b->finished = 1;
}

static bson_buffer * bson_append_estart( bson_buffer * b , int type , const char * name , const int dataSize ){
    const int sl = strlen(name) + 1;
    if ( ! bson_ensure_space( b , 1 + sl + dataSize ) )
        return 0;
    bson_append_byte( b , (char)type );
    bson_append( b , name , sl );
    return b;
}

/* ----------------------------
   BUILDING TYPES
   ------------------------------ */

bson_buffer * bson_append_int( bson_buffer * b , const char * name , const int i ){
    if ( ! bson_append_estart( b , bson_int , name , 4 ) ) return 0;
    bson_append32( b , &i );
    return b;
}
bson_buffer * bson_append_long( bson_buffer * b , const char * name , const int64_t i ){
    if ( ! bson_append_estart( b , bson_long , name , 8 ) ) return 0;
    bson_append64( b , &i );
    return b;
}
bson_buffer * bson_append_double( bson_buffer * b , const char * name , const double d ){
    if ( ! bson_append_estart( b , bson_double , name , 8 ) ) return 0;
    bson_append64( b , &d );
    return b;
}
bson_buffer * bson_append_bool( bson_buffer * b , const char * name , const bson_bool_t i ){
    if ( ! bson_append_estart( b , bson_bool , name , 1 ) ) return 0;
    bson_append_byte( b , i != 0 );
    return b;
}
bson_buffer * bson_append_null( bson_buffer * b , const char * name ){
    if ( ! bson_append_estart( b , bson_null , name , 0 ) ) return 0;
    return b;
}
bson_buffer * bson_append_undefined( bson_buffer * b , const char * name ){
    if ( ! bson_append_estart( b , bson_undefined , name , 0 ) ) return 0;
    return b;
}
bson_buffer * bson_append_string_base( bson_buffer * b , const char * name , const char * value , bson_type type){
    int sl = strlen( value ) + 1;
    if ( ! bson_append_estart( b , type , name , 4 + sl ) ) return 0;
    bson_append32( b , &sl);
    bson_append( b , value , sl );
    return b;
}
bson_buffer * bson_append_string( bson_buffer * b , const char * name , const char * value ){
    return bson_append_string_base(b, name, value, bson_string);
}
bson_buffer * bson_append_symbol( bson_buffer * b , const char * name , const char * value ){
    return bson_append_string_base(b, name, value, bson_symbol);
}
bson_buffer * bson_append_code( bson_buffer * b , const char * name , const char * value ){
    return bson_append_string_base(b, name, value, bson_code);
}

bson_buffer * bson_append_code_w_scope( bson_buffer * b , const char * name , const char * code , const bson * scope){
    int sl = strlen(code) + 1;
    int size = 4 + 4 + sl + bson_size(scope);
    if (!bson_append_estart(b, bson_codewscope, name, size)) return 0;
    bson_append32(b, &size);
    bson_append32(b, &sl);
    bson_append(b, code, sl);
    bson_append(b, scope->data, bson_size(scope));
    return b;
}

bson_buffer * bson_append_binary( bson_buffer * b, const char * name, char type, const char * str, int len ){
    if ( ! bson_append_estart( b , bson_bindata , name , 4+1+len ) ) return 0;
    bson_append32(b, &len);
    bson_append_byte(b, type);
    bson_append(b, str, len);
    return b;
}
bson_buffer * bson_append_oid( bson_buffer * b , const char * name , const bson_oid_t * oid ){
    if ( ! bson_append_estart( b , bson_oid , name , 12 ) ) return 0;
    bson_append( b , oid , 12 );
    return b;
}
bson_buffer * bson_append_new_oid( bson_buffer * b , const char * name ){
    bson_oid_t oid;
    bson_oid_gen(&oid);
    return bson_append_oid(b, name, &oid);
}

bson_buffer * bson_append_regex( bson_buffer * b , const char * name , const char * pattern, const char * opts ){
    const int plen = strlen(pattern)+1;
    const int olen = strlen(opts)+1;
    if ( ! bson_append_estart( b , bson_regex , name , plen + olen ) ) return 0;
    bson_append( b , pattern , plen );
    bson_append( b , opts , olen );
    return b;
}

bson_buffer * bson_append_bson( bson_buffer * b , const char * name , const bson* bson){
    if ( ! bson_append_estart( b , bson_object , name , bson_size(bson) ) ) return 0;
    bson_append( b , bson->data , bson_size(bson) );
    return b;
}

bson_buffer * bson_append_element( bson_buffer * b, const char * name_or_null, const bson_iterator* elem){
    bson_iterator next = *elem;
    int size;

    bson_iterator_next(&next);
    size = next.cur - elem->cur;

    if (name_or_null == NULL){
        bson_ensure_space(b, size);
        bson_append(b, elem->cur, size);
    }else{
        int data_size = size - 1 - strlen(bson_iterator_key(elem));
        bson_append_estart(b, elem->cur[0], name_or_null, data_size);
        bson_append(b, name_or_null, strlen(name_or_null));
        bson_append(b, bson_iterator_value(elem), data_size);
    }

    return b;
}

bson_buffer * bson_append_date( bson_buffer * b , const char * name , bson_date_t millis ){
    if ( ! bson_append_estart( b , bson_date , name , 8 ) ) return 0;
    bson_append64( b , &millis );
    return b;
}

bson_buffer * bson_append_time_t( bson_buffer * b , const char * name , time_t secs){
    return bson_append_date(b, name, (bson_date_t)secs * 1000);
}

bson_buffer * bson_append_start_object( bson_buffer * b , const char * name ){
    if ( ! bson_append_estart( b , bson_object , name , 5 ) ) return 0;
    b->stack[ b->stackPos++ ] = b->cur - b->buf;
    bson_append32( b , &zero );
    return b;
}

bson_buffer * bson_append_start_array( bson_buffer * b , const char * name ){
    if ( ! bson_append_estart( b , bson_array , name , 5 ) ) return 0;
    b->stack[ b->stackPos++ ] = b->cur - b->buf;
    bson_append32( b , &zero );
    return b;
}

bson_buffer * bson_append_finish_object( bson_buffer * b ){
    char * start;
    int i;
    if ( ! bson_ensure_space( b , 1 ) ) return 0;
    bson_append_byte( b , 0 );
    
    start = b->buf + b->stack[ --b->stackPos ];
    i = b->cur - start;
    bson_little_endian32(start, &i);

    return b;
}

void * bson_malloc(int size){
    void* p = malloc(size);
    if (!p) {
        bson_fatal_msg(0, "malloc() failed");
        return 0;
    }

    return p;
}

static bson_err_handler err_handler = NULL;

bson_err_handler set_bson_err_handler(bson_err_handler func){
    bson_err_handler old = err_handler;
    err_handler = func;
    return old;
}

void bson_fatal( int ok ){
    bson_fatal_msg(ok, "");
}

int bson_fatal_msg( int ok , const char* msg){
    if (ok)
        return 1;

    if (err_handler){
        err_handler(msg);
        return 0;
    }

    fprintf( stderr , "error: %s\n" , msg );
    exit(-5);
}

const char bson_numstrs[1000][4] = {
    "0",  "1",  "2",  "3",  "4",  "5",  "6",  "7",  "8",  "9",
    "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
    "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
    "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
    "40", "41", "42", "43", "44", "45", "46", "47", "48", "49",
    "50", "51", "52", "53", "54", "55", "56", "57", "58", "59",
    "60", "61", "62", "63", "64", "65", "66", "67", "68", "69",
    "70", "71", "72", "73", "74", "75", "76", "77", "78", "79",
    "80", "81", "82", "83", "84", "85", "86", "87", "88", "89",
    "90", "91", "92", "93", "94", "95", "96", "97", "98", "99",

    "100", "101", "102", "103", "104", "105", "106", "107", "108", "109",
    "110", "111", "112", "113", "114", "115", "116", "117", "118", "119",
    "120", "121", "122", "123", "124", "125", "126", "127", "128", "129",
    "130", "131", "132", "133", "134", "135", "136", "137", "138", "139",
    "140", "141", "142", "143", "144", "145", "146", "147", "148", "149",
    "150", "151", "152", "153", "154", "155", "156", "157", "158", "159",
    "160", "161", "162", "163", "164", "165", "166", "167", "168", "169",
    "170", "171", "172", "173", "174", "175", "176", "177", "178", "179",
    "180", "181", "182", "183", "184", "185", "186", "187", "188", "189",
    "190", "191", "192", "193", "194", "195", "196", "197", "198", "199",

    "200", "201", "202", "203", "204", "205", "206", "207", "208", "209",
    "210", "211", "212", "213", "214", "215", "216", "217", "218", "219",
    "220", "221", "222", "223", "224", "225", "226", "227", "228", "229",
    "230", "231", "232", "233", "234", "235", "236", "237", "238", "239",
    "240", "241", "242", "243", "244", "245", "246", "247", "248", "249",
    "250", "251", "252", "253", "254", "255", "256", "257", "258", "259",
    "260", "261", "262", "263", "264", "265", "266", "267", "268", "269",
    "270", "271", "272", "273", "274", "275", "276", "277", "278", "279",
    "280", "281", "282", "283", "284", "285", "286", "287", "288", "289",
    "290", "291", "292", "293", "294", "295", "296", "297", "298", "299",

    "300", "301", "302", "303", "304", "305", "306", "307", "308", "309",
    "310", "311", "312", "313", "314", "315", "316", "317", "318", "319",
    "320", "321", "322", "323", "324", "325", "326", "327", "328", "329",
    "330", "331", "332", "333", "334", "335", "336", "337", "338", "339",
    "340", "341", "342", "343", "344", "345", "346", "347", "348", "349",
    "350", "351", "352", "353", "354", "355", "356", "357", "358", "359",
    "360", "361", "362", "363", "364", "365", "366", "367", "368", "369",
    "370", "371", "372", "373", "374", "375", "376", "377", "378", "379",
    "380", "381", "382", "383", "384", "385", "386", "387", "388", "389",
    "390", "391", "392", "393", "394", "395", "396", "397", "398", "399",

    "400", "401", "402", "403", "404", "405", "406", "407", "408", "409",
    "410", "411", "412", "413", "414", "415", "416", "417", "418", "419",
    "420", "421", "422", "423", "424", "425", "426", "427", "428", "429",
    "430", "431", "432", "433", "434", "435", "436", "437", "438", "439",
    "440", "441", "442", "443", "444", "445", "446", "447", "448", "449",
    "450", "451", "452", "453", "454", "455", "456", "457", "458", "459",
    "460", "461", "462", "463", "464", "465", "466", "467", "468", "469",
    "470", "471", "472", "473", "474", "475", "476", "477", "478", "479",
    "480", "481", "482", "483", "484", "485", "486", "487", "488", "489",
    "490", "491", "492", "493", "494", "495", "496", "497", "498", "499",

    "500", "501", "502", "503", "504", "505", "506", "507", "508", "509",
    "510", "511", "512", "513", "514", "515", "516", "517", "518", "519",
    "520", "521", "522", "523", "524", "525", "526", "527", "528", "529",
    "530", "531", "532", "533", "534", "535", "536", "537", "538", "539",
    "540", "541", "542", "543", "544", "545", "546", "547", "548", "549",
    "550", "551", "552", "553", "554", "555", "556", "557", "558", "559",
    "560", "561", "562", "563", "564", "565", "566", "567", "568", "569",
    "570", "571", "572", "573", "574", "575", "576", "577", "578", "579",
    "580", "581", "582", "583", "584", "585", "586", "587", "588", "589",
    "590", "591", "592", "593", "594", "595", "596", "597", "598", "599",

    "600", "601", "602", "603", "604", "605", "606", "607", "608", "609",
    "610", "611", "612", "613", "614", "615", "616", "617", "618", "619",
    "620", "621", "622", "623", "624", "625", "626", "627", "628", "629",
    "630", "631", "632", "633", "634", "635", "636", "637", "638", "639",
    "640", "641", "642", "643", "644", "645", "646", "647", "648", "649",
    "650", "651", "652", "653", "654", "655", "656", "657", "658", "659",
    "660", "661", "662", "663", "664", "665", "666", "667", "668", "669",
    "670", "671", "672", "673", "674", "675", "676", "677", "678", "679",
    "680", "681", "682", "683", "684", "685", "686", "687", "688", "689",
    "690", "691", "692", "693", "694", "695", "696", "697", "698", "699",

    "700", "701", "702", "703", "704", "705", "706", "707", "708", "709",
    "710", "711", "712", "713", "714", "715", "716", "717", "718", "719",
    "720", "721", "722", "723", "724", "725", "726", "727", "728", "729",
    "730", "731", "732", "733", "734", "735", "736", "737", "738", "739",
    "740", "741", "742", "743", "744", "745", "746", "747", "748", "749",
    "750", "751", "752", "753", "754", "755", "756", "757", "758", "759",
    "760", "761", "762", "763", "764", "765", "766", "767", "768", "769",
    "770", "771", "772", "773", "774", "775", "776", "777", "778", "779",
    "780", "781", "782", "783", "784", "785", "786", "787", "788", "789",
    "790", "791", "792", "793", "794", "795", "796", "797", "798", "799",

    "800", "801", "802", "803", "804", "805", "806", "807", "808", "809",
    "810", "811", "812", "813", "814", "815", "816", "817", "818", "819",
    "820", "821", "822", "823", "824", "825", "826", "827", "828", "829",
    "830", "831", "832", "833", "834", "835", "836", "837", "838", "839",
    "840", "841", "842", "843", "844", "845", "846", "847", "848", "849",
    "850", "851", "852", "853", "854", "855", "856", "857", "858", "859",
    "860", "861", "862", "863", "864", "865", "866", "867", "868", "869",
    "870", "871", "872", "873", "874", "875", "876", "877", "878", "879",
    "880", "881", "882", "883", "884", "885", "886", "887", "888", "889",
    "890", "891", "892", "893", "894", "895", "896", "897", "898", "899",

    "900", "901", "902", "903", "904", "905", "906", "907", "908", "909",
    "910", "911", "912", "913", "914", "915", "916", "917", "918", "919",
    "920", "921", "922", "923", "924", "925", "926", "927", "928", "929",
    "930", "931", "932", "933", "934", "935", "936", "937", "938", "939",
    "940", "941", "942", "943", "944", "945", "946", "947", "948", "949",
    "950", "951", "952", "953", "954", "955", "956", "957", "958", "959",
    "960", "961", "962", "963", "964", "965", "966", "967", "968", "969",
    "970", "971", "972", "973", "974", "975", "976", "977", "978", "979",
    "980", "981", "982", "983", "984", "985", "986", "987", "988", "989",
    "990", "991", "992", "993", "994", "995", "996", "997", "998", "999",
};

void bson_numstr(char* str, int i){
    if(i < 1000)
        memcpy(str, bson_numstrs[i], 4);
    else
        sprintf(str,"%d", i);
}
