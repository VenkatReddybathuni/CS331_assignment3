#include <stdio.h>

#define INFINITY 999

extern struct rtpkt {
  int sourceid;       /* id of sending router sending this pkt */
  int destid;         /* id of router to which pkt being sent 
                         (must be an immediate neighbor) */
  int mincost[4];    /* min cost to node 0 ... 3 */
  };

extern int TRACE;
extern int YES;
extern int NO;

struct distance_table 
{
  int costs[4][4];
} dt3;

/* students to write the following two routines, and maybe some others */

void rtinit3() 
{
  printf("rtinit3: \n");

  /* Initialize the distance table for node 0 with inf (999) */
  int i = 0;
  for (i = 0; i < 4; i++){
    int j = 0;
    for (j = 0; j < 4; j++){
      dt3.costs [i][j] = INFINITY;
    }
  }
  /* Set the costs for node 0 to itself and its neighbors */
  /* The costs are set as follows:
     cost to itself = 0
     cost to node 0 = 7
     cost to node 2 = 2
   */
  dt3.costs [0][0] = 7;
  dt3.costs [2][2] = 2;
  dt3.costs [3][3] = 0;

  /*send its directly-connected neighbors he cost of it minimum cost paths*/
  struct rtpkt updatepacket;
  updatepacket.sourceid = 3;

  int ind = 0;
  for (ind = 0; ind < 4; ind++)
    updatepacket.mincost [ind] = dt3.costs[ind][ind];

  /* Send the update packet to all directly connected neighbors */
  updatepacket.destid = 0;
  tolayer2(updatepacket);

  updatepacket.destid = 2;
  tolayer2(updatepacket);


  printf("Node 3 sent the following packet {7,2,0,%d} to Node 0 and 2 \n", INFINITY);
  printdt3(&dt3);
}


void rtupdate3(rcvdpkt)
  struct rtpkt *rcvdpkt;
{
  printf("rtupdate3: \n");
  
  int neighborid = rcvdpkt->sourceid;  // ID of the neighbor that sent this update
  int ind = 0;
  int updateInLinkCost = 0;  // Flag to track if our minimum costs change
  int * neighborCosts = rcvdpkt->mincost;  // The neighbor's distance vector

  printf("Received packet: {%d,%d,%d,%d} \n", neighborCosts[0],neighborCosts[1],neighborCosts[2],neighborCosts[3]);

  /* Update our distance table based on the received distance vector */
  for (ind = 0; ind < 4; ind++){
    /* Apply the Bellman-Ford equation for Distance Vector Routing:
     * D_x(y) = min_v { c(x,v) + D_v(y) }
     * 
     * Where:
     * - ind represents destination node y
     * - neighborid represents the neighbor node v
     * - dt3.costs[neighborid][neighborid] is our cost c(x,v) to reach neighbor v
     * - neighborCosts[ind] is neighbor v's cost D_v(y) to reach destination y
     * - dt3.costs[ind][neighborid] is our current cost to reach y via neighbor v
     */
    
    /*Calculate potential new cost to destination via this neighbor*/ 
    int maybeNewCost = dt3.costs[neighborid][neighborid] + neighborCosts[ind];
    
    /*If this new path is better than our current path via this neighbor*/ 
    if(maybeNewCost < dt3.costs[ind][neighborid]){
      // Update our distance table with this better path
      dt3.costs[ind][neighborid] = maybeNewCost;
      
      // Mark that our distance vector has changed and we need to notify neighbors
      updateInLinkCost = 1;
    }
  }

    // If any route costs have changed after processing the received update,
  // we need to notify our neighbors about our updated distance vector
  if (updateInLinkCost == 1) {

    printf("There is a LINK COST CHANGE: Node 3 will send updates to Node 0 and 2. \n\n");

    // Create a new routing packet to send our updated distance vector
    struct rtpkt updatepacket;
    updatepacket.sourceid = 3;  // Packet is from this node (node 0)

    // Calculate our new distance vector (minimum cost to each destination)
    // This array will contain our shortest path cost to each destination node
    int distanceVector[4];
    int minCost = INFINITY;  // Initialize to "infinity"

    /* Calculate the minimum cost to each destination considering all possible next hops
     * The distance vector algorithm finds the shortest path to each destination by 
     * examining all possible routes through each neighbor
     */
    int i, j;
    for (i = 0; i < 4; i++) {  // i = destination node
      for (j = 0; j < 4; j++) { // j = neighbor/next hop node
        
        /* For each destination i, check all possible next hops j
         * and find the one that offers the lowest total cost.
         * This implements the key part of the Bellman-Ford equation:
         * D(x,y) = min{c(x,v) + D(v,y)} for all neighbors v
         */
        if (dt3.costs[i][j] < minCost)
          minCost = dt3.costs[i][j];
      }

      // Store the minimum cost to reach destination i in our distance vector
      distanceVector[i] = minCost;
      minCost = INFINITY;  // Reset minCost for the next destination
    }

    for (i = 0; i < 4; i++) {
      dt3.costs[i][i] = distanceVector[i];
    }

    // Copy our calculated distance vector into the outgoing packet
    for (i = 0; i < 4; i++)
      updatepacket.mincost[i] = distanceVector[i];

    /* Send the updated distance vector to all neighbors
     * In distance vector routing, nodes only exchange information with 
     * directly connected neighbors. This is a key characteristic of the
     * distributed Bellman-Ford algorithm.
     */
    
    // Send to node 1
    updatepacket.destid = 0;
    tolayer2(updatepacket);
    
    // Send to node 2
    updatepacket.destid = 2;
    tolayer2(updatepacket);


    // Log the outgoing packet contents and current distance table state
    printf("Node 3 sent the following packe {%d,%d,%d,%d} to Node 0 and 2. \n", 
           distanceVector[0], distanceVector[1], distanceVector[2], distanceVector[3]);
    printdt3(&dt3);

  } // End of update propagation to neighbors
  printf("\n\n");
}


printdt3(dtptr)
  struct distance_table *dtptr;
  
{
  printf("             via     \n");
  printf("   D3 |    0     2 \n");
  printf("  ----|-----------\n");
  printf("     0|  %3d   %3d\n",dtptr->costs[0][0], dtptr->costs[0][2]);
  printf("dest 1|  %3d   %3d\n",dtptr->costs[1][0], dtptr->costs[1][2]);
  printf("     2|  %3d   %3d\n",dtptr->costs[2][0], dtptr->costs[2][2]);

}






