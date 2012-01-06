CC ?= gcc

INCLUDE_DIR = .

CFLAGS += -I$(INCLUDE_DIR) -g -Wall -Werror
LDFLAGS += -lm -lzmq

OBJ_DIR = obj
BIN_DIR = bin

BSON_DEPS = bson/bson.h bson/platform_hacks.h

DEPS = remotecv_ss.h
OBJ = $(OBJ_DIR)/remotecv_ss.o $(OBJ_DIR)/log_utils.o $(OBJ_DIR)/detector.o \
	  $(OBJ_DIR)/bson.o $(OBJ_DIR)/image_data.o

ifndef DEBUG
	CFLAGS += -O3
endif

$(BIN_DIR)/remotecv_ss: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LDFLAGS)

$(OBJ_DIR)/bson.o: bson/bson.c $(BSON_DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

$(OBJ_DIR)/%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

clean:
	rm -f $(OBJ_DIR)/*.o $(BIN_DIR)/remotecv_ss
