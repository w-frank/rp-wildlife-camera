//
//  ViewController.m
//  RasPiRemote
//
//  Created by Will Frank on 02/12/2017.
//  Copyright (c) 2017 Will Frank. All rights reserved.
//

#import "ViewController.h"

@interface ViewController ()

@end

@implementation ViewController

@synthesize port, host, connect, disconnect, status;

#pragma mark - View controller lifecycle

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view, typically from a nib.
    
    [status setText:@"Not connected"];
    
    // Load user defaults
    if ([[NSUserDefaults standardUserDefaults] objectForKey:@"com.willfrank.raspiremote.host"] != nil) {
        [host setText:[[NSUserDefaults standardUserDefaults] objectForKey:@"com.willfrank.raspiremote.host"]];
    }
    if ([[NSUserDefaults standardUserDefaults] objectForKey:@"com.willfrank.raspiremote.port"] != nil) {
        [port setText:[[NSUserDefaults standardUserDefaults] objectForKey:@"com.willfrank.raspiremote.port"]];
    }

}

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

#pragma mark - Actions

- (IBAction)turnLeft:(id)sender {
    NSString *response  = @"P7H";
	NSData *data = [[NSData alloc] initWithData:[response dataUsingEncoding:NSASCIIStringEncoding]];
	[_outputStream write:[data bytes] maxLength:[data length]];
}

- (IBAction)turnRight:(id)sender {
    NSString *response  = @"P7L";
	NSData *data = [[NSData alloc] initWithData:[response dataUsingEncoding:NSASCIIStringEncoding]];
	[_outputStream write:[data bytes] maxLength:[data length]];
}

- (IBAction)stop:(id)sender {
    NSString *response  = @"stop";
	NSData *data = [[NSData alloc] initWithData:[response dataUsingEncoding:NSASCIIStringEncoding]];
	[_outputStream write:[data bytes] maxLength:[data length]];
}

- (IBAction)doConnect:(id)sender {
    // Save user defaults
    NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
    [defaults setObject:[host text] forKey:@"com.willfrank.raspiremote.host"];
    [defaults setObject:[port text] forKey:@"com.willfrank.raspiremote.port"];
    [defaults synchronize];
    
    [[self host] resignFirstResponder];
    [[self port] resignFirstResponder];
    
    [self doDisconnect:nil];
    [self initNetworkCommunication];
    _connectInProgress = YES;
    
    [status setText:@"Connection in progress…"];
    [self performSelectorInBackground:@selector(waitForConnection:) withObject:nil];
}

- (IBAction)doDisconnect:(id)sender {
    [[self host] resignFirstResponder];
    [[self port] resignFirstResponder];

    [_outputStream close];
    
    _connectInProgress = NO;
    
    [status setText:@"Not connected"];
}

#pragma mark - Misc

- (void) waitForConnection:(id) sender {
    @autoreleasepool {
        while ([_outputStream streamStatus] != NSStreamStatusOpen && _connectInProgress) {
            [status performSelectorOnMainThread:@selector(setText:) withObject:@"Connection in progress…" waitUntilDone:YES];
        }
        if (_connectInProgress) {
            [status performSelectorOnMainThread:@selector(setText:) withObject:[NSString stringWithFormat:@"Connected to %@:%@", [self.host text], [self.port text]] waitUntilDone:YES];
        } else {
            [status performSelectorOnMainThread:@selector(setText:) withObject:@"Not connected" waitUntilDone:YES];
        }
    }
}

- (void)initNetworkCommunication {
    CFReadStreamRef readStream;
    CFWriteStreamRef writeStream;
    CFStreamCreatePairWithSocketToHost(NULL, (CFStringRef)CFBridgingRetain([self.host text]), [[self.port text] intValue], &readStream, &writeStream);
    _outputStream = (NSOutputStream *)CFBridgingRelease(writeStream);
    
    [_outputStream setDelegate:self];
    
    [_outputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
    
    [_outputStream open];
}

@end
