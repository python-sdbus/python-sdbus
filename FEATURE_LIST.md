## Encode and check functions

- [ ] Interface
- [ ] Service
- [ ] Object
- [ ] Member

## SdBus

### Creating bus connections

- [X] Default bus
- [ ] Default user bus
- [ ] Default system bus
- [ ] Open at file path
- [ ] Open remote with hostname
- [ ] Open at container (machinectl)

### Setting and getting bus properties

- [ ] Bus description
- [ ] Interactive authorization
- [ ] Unique name
- [ ] Call timeout

## SdBusInterface

### Attributes that can be declared

- [X] Method calls
- [ ] Signals
- [ ] Property
- [ ] Writable property

## SdBusMessage
- [ ] Reply with error (by passing exception)
- [ ] Credentials
- [ ] Sensitive data

### SdBusMessage add types
- [X] byte 'y'
- [X] boolean 'b'
- [X] 16 bit int 'n'
- [X] 16 bit unsigned 'q'
- [X] 32 bit int 'i'
- [X] 32 bit unsigned 'u'
- [X] 64 bit int 'x'
- [X] 64 bit unsigned 't'
- [X] double 'd'
- [X] string 's'
- [X] object path 'o'
- [X] signature 'g'
- [X] file descriptor 'h'
- [X] array 'a'
- [X] variant 'v'
- [X] struct '()'
- [X] dict '{}'

### SdBusMessage read types
- [X] bytes 'y'
- [X] boolean 'b'
- [X] 16 bit int 'n'
- [X] 16 bit unsigned 'q'
- [X] 32 bit int 'i'
- [X] 32 bit unsigned 'u'
- [X] 64 bit int 'x'
- [X] 64 bit unsigned 't'
- [X] double 'd'
- [X] string 's'
- [X] object path 'o'
- [X] signature 'g'
- [X] file descriptor 'h'
- [ ] array 'a'
- [ ] variant 'v'
- [ ] struct '()'
- [ ] dict '{}'